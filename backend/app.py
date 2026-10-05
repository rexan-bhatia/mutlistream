"""Flask application for the local MusicStream demo."""

import json
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS


PROJECT_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = PROJECT_DIR / "frontend"
DATA_FILE = Path(__file__).resolve().parent / "data" / "songs.json"
AUDIO_DIR = Path(__file__).resolve().parent / "audio"

app = Flask(__name__)
CORS(app)


def load_songs():
    """Load the demo catalogue from its JSON data file."""
    with DATA_FILE.open(encoding="utf-8") as songs_file:
        return json.load(songs_file)


@app.get("/")
def home():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.get("/api/status")
def status():
    return jsonify({"status": "ok", "application": "MusicStream"})


@app.get("/api/songs")
def get_songs():
    return jsonify(load_songs())


@app.get("/api/songs/<int:song_id>")
def get_song(song_id):
    song = next((item for item in load_songs() if item["id"] == song_id), None)
    if song is None:
        return jsonify({"error": "Song not found"}), 404
    return jsonify(song)


@app.get("/api/search")
def search_songs():
    query = request.args.get("q", "").strip().casefold()
    if not query:
        return jsonify([])

    searchable_fields = ("title", "artist", "album", "genre")
    results = [
        song
        for song in load_songs()
        if any(query in song[field].casefold() for field in searchable_fields)
    ]
    return jsonify(results)


@app.get("/api/artists")
def get_artists():
    songs = load_songs()
    artists = sorted({song["artist"] for song in songs}, key=str.casefold)
    return jsonify(artists)


@app.get("/audio/<path:filename>")
def get_audio(filename):
    return send_from_directory(
     AUDIO_DIR,
     filename,
     mimetype="audio/wav"
    )


@app.get("/<path:filename>")
def frontend_asset(filename):
    return send_from_directory(FRONTEND_DIR, filename)


@app.errorhandler(404)
def handle_not_found(error):
    if request.path.startswith("/api/"):
        return jsonify({"error": "API endpoint not found"}), 404
    return "Page not found", 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8083, debug=False)
