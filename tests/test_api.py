import sys
from pathlib import Path

import pytest


PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR / "backend"))

from app import app  # noqa: E402


@pytest.fixture()
def client():
    app.config.update(TESTING=True)
    with app.test_client() as test_client:
        yield test_client


def test_homepage_is_served(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"MusicStream" in response.data


def test_status_endpoint(client):
    response = client.get("/api/status")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok", "application": "MusicStream"}


def test_get_all_songs(client):
    response = client.get("/api/songs")
    assert response.status_code == 200
    assert len(response.get_json()) >= 10


def test_get_single_song(client):
    response = client.get("/api/songs/1")
    assert response.status_code == 200
    assert response.get_json()["title"] == "Summer Vibes"


def test_search_song(client):
    response = client.get("/api/search?q=summer")
    assert response.status_code == 200
    assert [song["title"] for song in response.get_json()] == ["Summer Vibes"]


def test_invalid_song_id(client):
    response = client.get("/api/songs/99999")
    assert response.status_code == 404
    assert response.get_json() == {"error": "Song not found"}


@pytest.mark.parametrize("url", ["/api/search", "/api/search?q=", "/api/search?q=%20%20"])
def test_empty_search_returns_no_results(client, url):
    response = client.get(url)
    assert response.status_code == 200
    assert response.get_json() == []


def test_unknown_api_route_returns_json_404(client):
    response = client.get("/api/not-a-route")
    assert response.status_code == 404
    assert response.get_json() == {"error": "API endpoint not found"}


def test_artists_endpoint(client):
    response = client.get("/api/artists")
    assert response.status_code == 200
    assert "Luna Harbor" in response.get_json()


def test_missing_audio_is_a_404(client):
    response = client.get("/audio/not-present.mp3")
    assert response.status_code == 404


def test_demo_audio_is_available_for_every_song(client):
    for song in client.get("/api/songs").get_json():
        response = client.get(song["audio_url"])
        assert response.status_code == 200
        assert response.data.startswith(b"RIFF")
        assert response.mimetype == "audio/wav"
