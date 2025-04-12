from flask import Flask, render_template, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from transformers import pipeline
import re

app = Flask(__name__)

# Initialize the summarization pipeline with a lightweight model
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-6-6")

def extract_video_id(url):
    """
    Extracts the video ID from a YouTube URL.
    """
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, url)
    return match.group(1) if match else None

def get_transcript(video_id):
    """
    Retrieves the transcript for a given YouTube video ID.
    """
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([entry['text'] for entry in transcript])
    except Exception as e:
        return None

def summarize_text(text):
    """
    Summarizes the provided text using the initialized summarizer.
    """
    # Split text into manageable chunks
    max_chunk = 500
    chunks = [text[i:i+max_chunk] for i in range(0, len(text), max_chunk)]
    summary = ""
    for chunk in chunks:
        summarized = summarizer(chunk, max_length=100, min_length=30, do_sample=False)
        summary += summarized[0]['summary_text'] + " "
    return summary.strip()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        video_id = extract_video_id(url)
        if not video_id:
            return jsonify({'error': 'Invalid YouTube URL.'})
        transcript = get_transcript(video_id)
        if not transcript:
            return jsonify({'error': 'Transcript not available for this video.'})
        summary = summarize_text(transcript)
        return jsonify({'summary': summary})
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=False)