from flask import Flask, request, jsonify, render_template
import requests
from bs4 import BeautifulSoup
import threading
import time

app = Flask(__name__)

transcript_cache = {}
cache_lock = threading.Lock()

@app.route("/")
def home():
    return render_template("index.html")  # or remove if not using

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

def fetch_transcript_from_mirror(video_id):
    try:
        url = f"https://youtubetranscript.com/?v={video_id}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        divs = soup.select("div#transcript > div")
        transcript = " ".join(div.text.strip() for div in divs)
        return transcript if transcript else None

    except Exception as e:
        print("Mirror fetch failed:", e)
        return None

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

    time.sleep(1.5)  # prevent abuse
    transcript = fetch_transcript_from_mirror(video_id)

    if not transcript:
        return jsonify({"error": "Transcript not available."}), 404

    cache_transcript(video_id, transcript)
    return jsonify({"transcript": transcript})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)