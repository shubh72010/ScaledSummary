from flask import Flask, request, jsonify, render_template
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import time
import threading
import hashlib

app = Flask(name)

transcript_cache = {} cache_lock = threading.Lock()

@app.route("/") def home(): return render_template("index.html")

def get_cached_transcript(video_id): with cache_lock: if video_id in transcript_cache: return transcript_cache[video_id] return None

def cache_transcript(video_id, transcript): with cache_lock: transcript_cache[video_id] = transcript

@app.route("/summary", methods=["POST"]) def get_summary(): data = request.get_json() video_url = data.get("url", "") video_id = extract_video_id(video_url)

if not video_id:
    return jsonify({"error": "Invalid YouTube URL."}), 400

cached = get_cached_transcript(video_id)
if cached:
    return jsonify({"transcript": cached})

try:
    # Delay to avoid hammering YouTube
    time.sleep(1.5)
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    text = " ".join([entry["text"] for entry in transcript])
    cache_transcript(video_id, text)
    return jsonify({"transcript": text})
except (TranscriptsDisabled, NoTranscriptFound):
    return jsonify({"error": "Transcript not available for this video."}), 404
except Exception as e:
    return jsonify({"error": str(e)}), 400

def extract_video_id(url): if "v=" in url: return url.split("v=")[-1].split("&")[0] elif "youtu.be/" in url: return url.split("youtu.be/")[-1].split("?")[0] return None

if name == "main": app.run(host="0.0.0.0", port=5000)

