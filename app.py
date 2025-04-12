from flask import Flask, request, jsonify, render_template
from youtube_transcript_api import YouTubeTranscriptApi
from transformers import pipeline
from urllib.parse import urlparse, parse_qs

app = Flask(__name__)
summarizer = pipeline("summarization")

def extract_video_id(url):
    parsed_url = urlparse(url)
    if parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:]
    elif parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
        if parsed_url.path == '/watch':
            return parse_qs(parsed_url.query).get('v', [None])[0]
        elif parsed_url.path.startswith('/embed/'):
            return parsed_url.path.split('/')[2]
        elif parsed_url.path.startswith('/v/'):
            return parsed_url.path.split('/')[2]
    return None

def fetch_transcript(video_url):
    video_id = extract_video_id(video_url)
    if not video_id:
        raise ValueError("Invalid YouTube URL")
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    return " ".join([entry['text'] for entry in transcript])

def summarize_text(text):
    max_chunk = 1000
    chunks = [text[i:i+max_chunk] for i in range(0, len(text), max_chunk)]
    summary = ""
    for chunk in chunks:
        summary += summarizer(chunk, max_length=130, min_length=30, do_sample=False)[0]['summary_text'] + " "
    return summary.strip()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        video_url = request.form.get("url", "").strip()
        if video_url.lower() == "ling guli guli guli wantang wu":
            return jsonify({"summary": "🎉 Easter Egg Unlocked: You have the magic words! 🎉"})
        try:
            transcript = fetch_transcript(video_url)
            summary = summarize_text(transcript)
            return jsonify({"summary": summary})
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    return render_template("index.html")