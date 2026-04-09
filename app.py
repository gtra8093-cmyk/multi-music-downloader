from flask import Flask, render_template, request, jsonify
import os
import subprocess
import threading
import uuid

app = Flask(__name__)
DOWNLOAD_FOLDER = 'downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def detect_platform(url):
    url_lower = url.lower()
    if 'youtube.com' in url_lower or 'youtu.be' in url_lower:
        return 'youtube'
    elif 'spotify.com' in url_lower:
        return 'spotify'
    elif 'jiosaavn.com' in url_lower or 'saavn.com' in url_lower:
        return 'jiosaavn'
    return 'unknown'

def download_youtube(url, download_id):
    try:
        folder = os.path.join(DOWNLOAD_FOLDER, download_id)
        os.makedirs(folder, exist_ok=True)
        cmd = [
            'yt-dlp', '-x', '--audio-format', 'mp3', '--audio-quality', '0',
            '--yes-playlist', '--embed-thumbnail', '--embed-metadata',
            '-o', f'{folder}/%(title)s.%(ext)s', url
        ]
        subprocess.run(cmd, check=True, timeout=1800)
        return "✅ YouTube playlist successfully downloaded!"
    except Exception as e:
        return f"❌ YouTube Error: {str(e)[:100]}"

def download_spotify(url, download_id):
    try:
        folder = os.path.join(DOWNLOAD_FOLDER, download_id)
        os.makedirs(folder, exist_ok=True)
        cmd = ['spotdl', url, '--output', folder, '--embed-metadata']
        subprocess.run(cmd, check=True, timeout=1800)
        return "✅ Spotify downloaded with metadata & cover art!"
    except Exception as e:
        return f"❌ Spotify Error: {str(e)[:100]}"

def download_jiosaavn(url, download_id):
    return "⚠️ JioSaavn abhi basic support mein hai. Better version jaldi add karenge."

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def start_download():
    url = request.form.get('url', '').strip()
    if not url:
        return jsonify({"error": "URL daal na zaroori hai"}), 400

    platform = detect_platform(url)
    if platform == 'unknown':
        return jsonify({"error": "Sirf YouTube, Spotify ya JioSaavn link allowed hai"}), 400

    download_id = str(uuid.uuid4())[:8]
    folder = os.path.join(DOWNLOAD_FOLDER, download_id)
    os.makedirs(folder, exist_ok=True)

    def run_download():
        if platform == 'youtube':
            msg = download_youtube(url, download_id)
        elif platform == 'spotify':
            msg = download_spotify(url, download_id)
        else:
            msg = download_jiosaavn(url, download_id)
        print(f"[{download_id}] {msg}")

    threading.Thread(target=run_download, daemon=True).start()

    return jsonify({
        "message": f"🚀 {platform.upper()} download shuru! Badi playlist mein 5-15 minute lag sakte hain.",
        "download_id": download_id
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
