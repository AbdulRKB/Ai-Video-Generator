from google import genai
import json, re, time, requests, gtts, os
from PIL import Image
from moviepy import *

GEMINI_API_KEY = "ENTER_YOUR_GEMINI_API_KEY"
CLOUDFLARE_ACCOUNT_ID = "ENTER_YOUR_CLOUDFLARE_ACCOUNT_ID"
CLOUDFLARE_API_TOKEN = "ENTER_YOUR_CLOUDFLARE_API_TOKEN"

client = genai.Client(api_key=GEMINI_API_KEY)

def ask_gemini(prompt):
    response = client.models.generate_content(model="gemini-2.0-flash",contents=prompt)
    return response.text

def generate_script(prompt):
    structured_prompt = f"""
        Create a video script based on this prompt: "{prompt}"
        
        Return a JSON structure with the following format:
        {{
            "title": "Video title",
            "description": "Brief video description",
            "scenes": [
                {{
                    "narration": "Text for scene 1",
                    "image_prompt": "Detailed image prompt for scene 1"
                }},
                // More scenes
            ]
        }}
        
        The script should have 5-8 scenes, each with narration of 2-3 sentences and a detailed image prompt.
        Make the image prompts highly descriptive for best results with an image generator. Make sure that its short enough so that the final video is less than 1 min. 
        """
    
    response = ask_gemini(structured_prompt)

    json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
    if json_match:
        response = json_match.group(1)
    else:
        json_match = re.search(r'({.*})', response, re.DOTALL)
        if json_match:
            response = json_match.group(1)
    try:
        script = json.loads(response)
        return script
    except json.JSONDecodeError as e:
        print(f"Error parsing script JSON: {e}")
        print(f"Raw script: {response}")
        raise e

def generate_image(prompt, filename):

    url = f"https://api.cloudflare.com/client/v4/accounts/d6e72b167cf0105a76867b8851e37461/ai/run/@cf/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}"
    }
    data = {
        "prompt": prompt
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        with open(filename, "wb") as file:
            file.write(response.content)
        print("Image downloaded successfully!")
    else:
        print(f"Error {response.status_code}: {response.text}")


def generate_images(script):
        print("Generating images for scenes...")
        image_paths = []
        
        for i, scene in enumerate(script["scenes"]):
            image_prompt = scene["image_prompt"]
            enhanced_prompt = f"High quality, detailed image: {image_prompt}. Photorealistic, high resolution."
            
            print(f"Generating image {i+1}/{len(script['scenes'])}: {image_prompt[:50]}...")
            
            try:
                image_path = str(f"scene_{i+1}.jpg")
                generate_image(enhanced_prompt, image_path)                
                
                image_paths.append(image_path)
                print(f"Image saved to {image_path}")
                
                # Avoid API rate limits
                time.sleep(1)
                
            except Exception as e:
                print(f"Error generating image for scene {i+1}: {e}")
                # Use a placeholder image
                placeholder_path = str(f"placeholder_{i+1}.jpg")
                Image.new('RGB', (1024, 768), color='gray').save(placeholder_path)
                image_paths.append(placeholder_path)
        
        return image_paths

def generate_narration_audio(script):
        print("Generating narration audio...")
        audio_paths = []
        
        for i, scene in enumerate(script["scenes"]):
            narration_text = scene["narration"]
            audio_path = str(f"narration_{i+1}.mp3")
            
            try:
                tts = gtts.gTTS(narration_text)

                tts.save(audio_path)
                audio_paths.append(audio_path)
                print(f"Audio saved to {audio_path}")
            except Exception as e:
                print(f"Error generating audio for scene {i+1}: {e}")
            time.sleep(0.5)
            
        return audio_paths


def create_video(script, image_paths, audio_paths):
        print("Creating video...")
        clips = []        
        for i, (image_path, audio_path) in enumerate(zip(image_paths, audio_paths)):
            if not os.path.exists(audio_path):
                duration = 5.0
                audio_clip = AudioClip(lambda t: 0, duration=duration)
            else:
                audio_clip = AudioFileClip(audio_path)
                duration = audio_clip.duration
                duration += 0.5
            
            img_clip = ImageClip(image_path).with_duration(duration)
            
            if os.path.exists(audio_path):
                img_clip = img_clip.with_audio(audio_clip)
            
            clips.append(img_clip)
        
        final_clip = concatenate_videoclips(clips, method="compose")
        final_clip = concatenate_videoclips([final_clip], method="compose")
        output_path = str("final_video.mp4")
        final_clip.write_videofile(output_path, fps=1, codec='libx264', audio_codec='aac', threads=8, preset="ultrafast")        
        print(f"Video saved to {output_path}")
        return output_path

def main():
    story_description = str(input("Enter a brief description about your story: "))
    script = generate_script(story_description)
    image_paths = generate_images(script)
    audio_paths = generate_narration_audio(script)
    create_video(script, image_paths, audio_paths)
    # delete all the images and audio files
    for image_path in image_paths: os.remove(image_path)
    for audio_path in audio_paths: os.remove(audio_path)

main()