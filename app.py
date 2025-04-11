import os
import re
import time
from flask import Flask, render_template, request
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, VideoUnavailable, TooManyRequests
from transformers import pipeline

app = Flask(__name__)

# Initialize multiple summarizer pipelines for fallback.
summarizers = []
try:
    summarizers.append(("t5-small", pipeline("summarization", model="t5-small", tokenizer="t5-small")))
except Exception as e:
    print("Error initializing t5-small:", e)
try:
    summarizers.append(("bart-large-cnn", pipeline("summarization", model="facebook/bart-large-cnn")))
except Exception as e:
    print("Error initializing bart-large-cnn:", e)
try:
    summarizers.append(("distilbart-cnn-12-6", pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")))
except Exception as e:
    print("Error initializing distilbart-cnn-12-6:", e)

def get_video_id(url):
    """
    Extract the YouTube video ID from a URL.
    """
    try:
        # Attempt to extract from query parameters
        pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        return None
    except Exception:
        return None

def fetch_transcript(video_url):
    """
    Fetch the transcript text from YouTube using the provided URL.
    Implements retry logic with exponential backoff for TooManyRequests errors.
    """
    video_id = get_video_id(video_url)
    if not video_id:
        return "Invalid YouTube URL."
    
    retries = 3
    backoff = 2
    for attempt in range(retries):
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            return " ".join([entry["text"] for entry in transcript])
        except TooManyRequests:
            time.sleep(backoff ** attempt)
        except TranscriptsDisabled:
            return "Transcripts are disabled for this video."
        except VideoUnavailable:
            return "Video is unavailable or private."
        except Exception as e:
            return f"Error: {str(e)}"
    return "Too many requests. Try again later."

def summarize_text(text):
    """
    Summarizes the input text using multiple models.
    If the text is long, it will be split into chunks.
    Each chunk is summarized by trying each summarizer in order until one succeeds.
    """
    max_chunk_length = 400  # Adjust based on model limits.
    
    def summarize_chunk(chunk):
        for name, summarizer in summarizers:
            try:
                result = summarizer("summarize: " + chunk, max_length=120, min_length=30, do_sample=False)[0]['summary_text']
                return result
            except Exception as e:
                print(f"Summarizer {name} failed for chunk: {e}")
                continue
        return "[Error in summarization]"
    
    if len(text) > max_chunk_length:
        chunks = [text[i:i+max_chunk_length] for i in range(0, len(text), max_chunk_length)]
        summarized_chunks = [summarize_chunk(chunk) for chunk in chunks]
        return " ".join(summarized_chunks)
    else:
        for name, summarizer in summarizers:
            try:
                result = summarizer("summarize: " + text, max_length=150, min_length=30, do_sample=False)[0]['summary_text']
                return result
            except Exception as e:
                print(f"Summarizer {name} failed: {e}")
                continue
    return "All summarization APIs are currently unavailable. Please try again later."

@app.route("/", methods=["GET", "POST"])
def index():
    summary = ""
    if request.method == "POST":
        video_url = request.form["video_url"]
        transcript = fetch_transcript(video_url)
        summary = summarize_text(transcript)
    return render_template("index.html", summary=summary)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)