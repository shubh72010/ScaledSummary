from flask import Flask, request, render_template
from youtube_transcript_api import YouTubeTranscriptApi
from transformers import pipeline

app = Flask(__name__)
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def get_transcript(video_id):
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    return " ".join([entry["text"] for entry in transcript])

@app.route("/", methods=["GET", "POST"])
def index():
    summary = ""
    error = ""
    if request.method == "POST":
        url = request.form["url"]
        try:
            video_id = url.split("v=")[-1].split("&")[0]
            full_text = get_transcript(video_id)
            if len(full_text) > 1024:
                chunks = [full_text[i:i+1024] for i in range(0, len(full_text), 1024)]
                summaries = [summarizer(chunk, max_length=120, min_length=30, do_sample=False)[0]['summary_text'] for chunk in chunks]
                summary = " ".join(summaries)
            else:
                summary = summarizer(full_text, max_length=150, min_length=30, do_sample=False)[0]["summary_text"]
        except Exception as e:
            error = f"Error: {e}"
    return render_template("index.html", summary=summary, error=error)

if __name__ == "__main__":
    app.run(debug=True)
