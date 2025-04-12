from flask import Flask, request, jsonify, render_template from youtube_transcript_api import YouTubeTranscriptApi

app = Flask(name)

@app.route("/") def index(): return render_template("index.html")

@app.route("/summary", methods=["POST"]) def get_summary(): data = request.get_json() video_url = data.get("url", "") if "v=" not in video_url: return jsonify({"error": "Invalid URL"}), 400

video_id = video_url.split("v=")[-1]

try:
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    text = " ".join([entry["text"] for entry in transcript])
    return jsonify({"transcript": text})
except Exception as e:
    return jsonify({"error": str(e)}), 500

if name == "main": import os port = int(os.environ.get("PORT", 5000)) app.run(host="0.0.0.0", port=port)

