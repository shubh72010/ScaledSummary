import os
import re
from flask import Flask, render_template, request
from youtube_transcript_api import YouTubeTranscriptApi
from transformers import pipeline

app = Flask(__name__)

# Initialize the summarizer pipeline with the T5-small model
summarizer = pipeline("summarization", model="t5-small", tokenizer="t5-small")

def get_video_id(url):
    """
    Extracts the video ID from YouTube URLs in various formats.
    """
    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11}).*",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def fetch_transcript(video_url):
    video_id = get_video_id(video_url)
    if not video_id:
        raise ValueError("Could not extract video ID from the URL.")
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    full_text = " ".join([entry["text"] for entry in transcript])
    return full_text

def summarize_text(text):
    # To avoid input length issues, break text into chunks if necessary.
    max_chunk_length = 400  # Adjust as needed based on model limits
    if len(text) > max_chunk_length:
        chunks = [text[i:i+max_chunk_length] for i in range(0, len(text), max_chunk_length)]
        summaries = [summarizer("summarize: " + chunk, max_length=120, min_length=30, do_sample=False)[0]['summary_text']
                     for chunk in chunks]
        return " ".join(summaries)
    else:
        return summarizer("summarize: " + text, max_length=150, min_length=30, do_sample=False)[0]['summary_text']

@app.route("/", methods=["GET", "POST"])
def index():
    summary = ""
    error = ""
    if request.method == "POST":
        url = request.form.get("url", "").strip()
        try:
            transcript = fetch_transcript(url)
            summary = summarize_text(transcript)
        except Exception as e:
            error = f"Error: {str(e)}"
    return render_template("index.html", summary=summary, error=error)

# Production-ready entry point (used by Gunicorn)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # Bind to all interfaces; necessary for Render
    app.run(host="0.0.0.0", port=port, debug=False)