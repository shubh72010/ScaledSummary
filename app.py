from flask import Flask, render_template, request
from youtube_transcript_api import YouTubeTranscriptApi
from transformers import pipeline

app = Flask(__name__)

summarizer = pipeline("summarization", model="t5-small", tokenizer="t5-small")

def get_video_id(url):
    import re
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    return match.group(1) if match else None

def fetch_transcript(video_url):
    video_id = get_video_id(video_url)
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    full_text = " ".join([x['text'] for x in transcript])
    return full_text

def summarize_text(text):
    # Break into chunks if needed
    max_len = 400
    chunks = [text[i:i+max_len] for i in range(0, len(text), max_len)]
    summaries = [summarizer("summarize: " + chunk)[0]['summary_text'] for chunk in chunks]
    return " ".join(summaries)

@app.route("/", methods=["GET", "POST"])
def index():
    summary = ""
    if request.method == "POST":
        url = request.form["url"]
        try:
            transcript = fetch_transcript(url)
            summary = summarize_text(transcript)
        except Exception as e:
            summary = f"Error: {str(e)}"
    return render_template("index.html", summary=summary)

if __name__ == "__main__":
    app.run(debug=True)