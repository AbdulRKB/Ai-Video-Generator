# 🧠 AI Video Generator

A Python script that automatically generates a short narrated video from a simple text.

---

## 🔧 Requirements

* Python 3.8+
* [Google Gemini API key](https://ai.google.dev/)
* [Cloudflare API token](https://dash.cloudflare.com/)
* Required Python packages:

  ```bash
  pip install google-generativeai requests gtts moviepy pillow
  ```

---

## 📁 Setup

1. Replace these values in the script:

```python
GEMINI_API_KEY = "ENTER_YOUR_GEMINI_API_KEY"
CLOUDFLARE_ACCOUNT_ID = "ENTER_YOUR_CLOUDFLARE_ACCOUNT_ID"
CLOUDFLARE_API_TOKEN = "ENTER_YOUR_CLOUDFLARE_API_TOKEN"
```

2. Run the script:

```bash
python app.py
```
