# 🎬 Videoly

**Paste a link. Skip the video. Get the gist.**

Videoly pulls the transcript off any YouTube video and hands it to Gemini to distill into a tight, readable summary, so you can decide in 10 seconds whether that 45-minute video is worth your time.

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue?logo=python&logoColor=white" alt="Python 3.9+">
  <img src="https://img.shields.io/badge/Streamlit-app-FF4B4B?logo=streamlit&logoColor=white" alt="Streamlit">
  <img src="https://img.shields.io/badge/Gemini-3.1_Flash--Lite-4285F4?logo=googlegemini&logoColor=white" alt="Gemini 3.1 Flash-Lite">

</p>

---

## What it does

1. You paste a YouTube URL — standard, short (`youtu.be`), Shorts, or `/live/` links all work.
2. Videoly fetches the video's transcript.
3. The transcript goes to **Gemini 3.1 Flash-Lite**, which returns a punchy ~250-word summary.
4. Thumbnail and summary land side-by-side so you can eyeball the video and read the takeaway in one glance.

No downloads, no ads, no watching at 2x speed and still missing the point.

---

## 🚀 Getting started

### 1. Clone and enter the project
```bash
git clone https://github.com/Arnaaavvv/videoly.git
cd videoly
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up your API key
Copy the example env file and drop in your own [Gemini API key](https://aistudio.google.com/app/apikey):
```bash
#.env
GOOGLE_API_KEY=your-key-here
```


### 4. Run it
```bash
streamlit run main.py
```
Then open the local URL Streamlit prints (usually `http://localhost:8501`).

---

## Tech stack

| Piece | Role |
|---|---|
| Streamlit | UI |
| youtube-transcript-api| Pulls the transcript |
| Gemini 3.1 Flash-Lite | Generates the summary |
| python-dotenv | Loads local secrets |

---

## ⚙️ Limits

- Videos with transcripts/captions disabled can't be summarized — that's a YouTube-side restriction, not a Videoly bug.
- Very long transcripts (60,000+ characters) are truncated before summarizing, to keep things fast and cheap.
- Summaries are generated fresh per video and cached for the session, re-running the same URL won't re-hit the API.

---
## Note : 
The AI summary may be imperfect. This project is experimental and created for fun.