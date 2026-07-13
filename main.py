from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi
from google import genai
from dotenv import load_dotenv
import streamlit as st
import os

load_dotenv()

st.set_page_config(
    page_title="Videoly Summarizer",
    page_icon="🎬",
    layout="centered",
)

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.error("GOOGLE_API_KEY is not set. Add it to your .env file.")
    st.stop()
client = genai.Client(api_key=api_key)

PROMPT = "You are a helpful YouTube video summarizer. Summarize the following transcript in a concise and informative manner, highlighting the key points and main ideas within 250 words. Provide a clear and engaging summary that captures the essence of the video content. The transcript is as follows : "

MAX_TRANSCRIPT_CHARS = 60_000  # ~15k words, caps cost on very long videos


# ---------- Styling ----------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@400;500&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: #cfe4f5;
        color: #1a1a1a;
    }

    .hero {
        text-align: center;
        padding: 2.4rem 1rem 1.6rem 1rem;
    }
    .hero h1 {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.4rem;
        font-weight: 700;
        color: #111111;
        margin-bottom: 0.3rem;
        letter-spacing: -0.02em;
    }
    .hero h1 span {
        color: #2b6ea3;
    }
    .hero p {
        color: #5c6b76;
        font-size: 1.02rem;
        margin-top: 0;
    }

    div[data-testid="stTextInput"] input {
        background-color: #ffffff;
        border: 1.5px solid #cfe0ea;
        border-radius: 10px;
        color: #1a1a1a;
        padding: 0.7rem 1rem;
        font-size: 1rem;
    }
    div[data-testid="stTextInput"] input:focus {
        border: 1.5px solid #2b6ea3;
        box-shadow: 0 0 0 3px rgba(43, 110, 163, 0.14);
    }

    .stButton > button {
        background: #111111;
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.65rem 1.6rem;
        font-weight: 500;
        font-size: 1rem;
        width: 100%;
        transition: background 0.15s ease, transform 0.15s ease;
    }
    .stButton > button:hover {
        background: #2b6ea3;
        transform: translateY(-1px);
        color: white;
    }

    .thumb-wrap {
        border-radius: 14px;
        overflow: hidden;
        border: 1px solid #cfe0ea;
        margin: 1.2rem 0;
        box-shadow: 0 4px 16px rgba(43, 110, 163, 0.08);
    }

    .summary-card {
        background: #ffffff;
        border: 1px solid #cfe0ea;
        border-left: 4px solid #2b6ea3;
        border-radius: 14px;
        padding: 1.6rem 1.8rem;
        margin-top: 1.2rem;
        box-shadow: 0 4px 16px rgba(43, 110, 163, 0.08);
    }
    .summary-card h3 {
        font-family: 'Space Grotesk', sans-serif;
        color: #111111;
        margin-top: 0;
        font-size: 1.15rem;
    }
    .summary-card p {
        color: #333333;
        line-height: 1.7;
        font-size: 1.02rem;
    }

    .footer-note {
        text-align: center;
        color: #8ba2b0;
        font-size: 0.85rem;
        margin-top: 2.5rem;
    }

    div[data-testid="stAlert"] {
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def extract_video_id(url: str):
    """Robustly pull the video ID out of standard, short, Shorts, and live YouTube URLs."""
    if not url:
        return None

    parsed = urlparse(url.strip())

    if parsed.hostname in ("youtu.be",):
        video_id = parsed.path.lstrip("/")
        return video_id or None

    if parsed.hostname in ("www.youtube.com", "youtube.com", "m.youtube.com"):
        path_parts = [p for p in parsed.path.split("/") if p]

        if path_parts and path_parts[0] in ("shorts", "live", "embed"):
            return path_parts[1] if len(path_parts) > 1 else None

        query_params = parse_qs(parsed.query)
        return query_params.get("v", [None])[0]

    return None


@st.cache_data(show_spinner=False)
def extract_transcript(video_id: str):
    """Fetch and flatten the transcript for a given video ID."""
    try:
        ytt_api = YouTubeTranscriptApi()
        fetched = ytt_api.fetch(video_id)
        transcript = " ".join(snippet.text for snippet in fetched)
        return transcript
    except Exception as e:
        st.error(f"Error extracting transcript: {e}")
        return None


@st.cache_data(show_spinner=False)
def generate_content(transcript: str, prompt: str):
    """Send the transcript + prompt to Gemini and return the summary text."""
    try:
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=prompt + transcript,
        )
        return response.text
    except Exception as e:
        st.error(f"Error generating summary: {e}")
        return None


# ---------- UI ----------
st.markdown(
    """
    <div class="hero">
        <h1>🎬 Videoly</h1>
        <p>Paste a YouTube link. Get the gist in seconds.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

youtube_url = st.text_input(
    "YouTube URL",
    placeholder="https://www.youtube.com/watch?v=...",
    label_visibility="collapsed",
)

video_id = None
if youtube_url:
    video_id = extract_video_id(youtube_url)
    if video_id:
        st.markdown('<div class="thumb-wrap">', unsafe_allow_html=True)
        st.image(f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("Couldn't recognize that as a valid YouTube URL.")

go = st.button("Summarize it")

if go:
    if not video_id:
        st.error("Please enter a valid YouTube URL first.")
    else:
        with st.spinner("Pulling the transcript..."):
            transcript = extract_transcript(video_id)

        if transcript:
            if len(transcript) > MAX_TRANSCRIPT_CHARS:
                st.info(
                    f"This video's transcript is long ({len(transcript):,} characters). "
                    f"Summarizing the first {MAX_TRANSCRIPT_CHARS:,} characters only."
                )
                transcript = transcript[:MAX_TRANSCRIPT_CHARS]

            with st.spinner("Thinking about the good parts..."):
                summary = generate_content(transcript, PROMPT)

            if summary:
                st.markdown(
                    f"""
                    <div class="summary-card">
                        <h3>📝 Summary</h3>
                        <p>{summary}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )