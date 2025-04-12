from flask import Flask, request, jsonify, render_template
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import threading
import time

app = Flask(__name__)

transcript_cache = {}
cache_lock = threading.Lock()

@app.route("/")
def home():
    return render_template("index.html")

def extract_video_id(url):
    if "v=" in url:
        return url.split("v=")[-1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[-1].split("?")[0]
    return None

def get_cached_transcript(video_id):
    with cache_lock:
        return transcript_cache.get(video_id)

def cache_transcript(video_id, transcript):
    with cache_lock:
        transcript_cache[video_id] = transcript

@app.route("/summary", methods=["POST"])
def get_summary():
    data = request.get_json()
    video_url = data.get("url", "")
    video_id = extract_video_id(video_url)

    if not video_id:
        return jsonify({"error": "Invalid YouTube URL."}), 400

    cached = get_cached_transcript(video_id)
    if cached:
        return jsonify({"transcript": cached})

    try:
        time.sleep(1.5)  # To avoid bot detection
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        full_text = " ".join([entry["text"] for entry in transcript])
        cache_transcript(video_id, full_text)
        return jsonify({"transcript": full_text})
    except (TranscriptsDisabled, NoTranscriptFound):
        return jsonify({"error": "Transcript not available for this video."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)