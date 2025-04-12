import os
import re
import time
import logging
from flask import Flask, render_template, request, jsonify
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    VideoUnavailable,
    TooManyRequests
)
from transformers import pipeline

# Setup logging with an Easter egg message
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("🐣 Welcome to the ScaledSummary Easter Egg Extravaganza!")

app = Flask(__name__)

# Initialize summarizer pipeline using T5-small (lightweight & efficient)
MODEL_NAME = os.environ.get("MODEL_NAME", "t5-small")
logger.info(f"Using summarization model: {MODEL_NAME}")
summarizer = pipeline("summarization", model=MODEL_NAME, tokenizer=MODEL_NAME, device=-1)

def get_video_id(url):
    """Extracts the YouTube video ID from the provided URL."""
    # Easter egg: if URL contains 'secretegg', return a classic dummy ID
    if "secretegg" in url.lower():
        logger.info("Easter Egg Found: Secret egg video!")
        return "dQw4w9WgXcQ"  # Rickroll!
    match = re.search(r"(?:v=|youtu\.be/)([0-9A-Za-z_-]{11})", url)
    return match.group(1) if match else None

def fetch_transcript(video_url):
    """Fetches transcript from YouTube with exponential backoff."""
    video_id = get_video_id(video_url)
    if not video_id:
        raise ValueError("Invalid YouTube URL. Try a secret egg?")
    retries = 3
    backoff = 2
    for attempt in range(retries):
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            full_text = " ".join(entry["text"] for entry in transcript)
            if len(transcript) < 3:
                logger.info("Easter Egg: Tiny transcript detected!")
            return full_text
        except TooManyRequests:
            sleep_time = backoff ** attempt
            logger.warning(f"Too many requests; retrying in {sleep_time} seconds...")
            time.sleep(sleep_time)
        except TranscriptsDisabled:
            raise ValueError("Transcripts are disabled for this video.")
        except VideoUnavailable:
            raise ValueError("Video is unavailable or private.")
    raise ValueError("Too many requests; please try again later.")

def smart_chunk(text, max_chunk_length=300):
    """
    Splits text into chunks at sentence boundaries while keeping each chunk
    under max_chunk_length. (Easter egg: if a chunk contains 'EasterEgg', it's intentional!)
    """
    sentences = re.split(r'(?<=[.!?]) +', text)
    chunks, current_chunk = [], ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) < max_chunk_length:
            current_chunk += (" " if current_chunk else "") + sentence
        else:
            chunks.append(current_chunk)
            current_chunk = sentence
    if current_chunk:
        chunks.append(current_chunk)
    return chunks

def summarize_text(text):
    """Summarizes the given text. Splits long text into chunks for memory efficiency."""
    max_chunk_length = 300  # smaller chunk size for lower memory usage

    def summarize_chunk(chunk):
        try:
            result = summarizer("summarize: " + chunk, max_length=120, min_length=30, do_sample=False)
            summary = result[0]['summary_text']
            if "egg" in summary.lower():
                logger.info("🥚 You found an Easter egg in the summary!")
            return summary
        except Exception as e:
            logger.error(f"Summarization error: {e}")
            return "[Error summarizing]"

    if len(text) > max_chunk_length:
        chunks = smart_chunk(text, max_chunk_length)
        logger.info(f"Splitting text into {len(chunks)} chunks for summarization.")
        summarized_chunks = [summarize_chunk(chunk) for chunk in chunks]
        return " ".join(summarized_chunks)
    else:
        return summarize_chunk(text)

@app.route("/", methods=["GET", "POST"])
def index():
    summary = ""
    error = ""
    if request.method == "POST":
        video_url = request.form.get("url", "").strip()
        logger.info(f"Received URL: {video_url}")
        # Hidden trigger: if user types the magic phrase, show a secret message.
        if video_url.lower() == "ling guli guli guli wantang wu":
            summary = "Easter Egg Unlocked: You have the magic words! 🎉"
        else:
            try:
                transcript = fetch_transcript(video_url)
                logger.info("Transcript fetched successfully.")
                summary = summarize_text(transcript)
                logger.info("Summarization completed.")
            except Exception as e:
                error = str(e)
                logger.error(f"Error processing request: {error}")
    return render_template("index.html", summary=summary, error=error)

@app.route("/secret", methods=["GET"])
def secret():
    """Secret endpoint for true Easter egg lovers."""
    return jsonify({"message": "Congratulations, you discovered the secret Easter Egg endpoint! 🥚🎉"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Starting ScaledSummary on port {port}")
    app.run(host="0.0.0.0", port=port)