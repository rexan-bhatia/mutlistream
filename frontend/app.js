const audio = document.querySelector("#audio-element");
const searchInput = document.querySelector("#search-input");
const trendingGrid = document.querySelector("#trending-grid");
const artistList = document.querySelector("#artist-list");
const searchResults = document.querySelector("#search-results");
const searchGrid = document.querySelector("#search-grid");
const searchEmpty = document.querySelector("#search-empty");
const playButton = document.querySelector("#play-button");
const progress = document.querySelector("#progress");
const audioNotice = document.querySelector("#audio-notice");

let songs = [];
let currentIndex = -1;
let noticeTimeout;

const palettes = [
  ["#c67559", "#e6b87e"], ["#6e8b7d", "#d5b38e"], ["#61528e", "#d77f9a"],
  ["#356477", "#8aa899"], ["#824f77", "#df9caf"], ["#3b7182", "#c8b982"],
];

function coverMarkup(song, index) {
  const palette = palettes[index % palettes.length];
  return `<div class="cover-art" style="background:linear-gradient(135deg,${palette[0]},${palette[1]})"><span class="cover-symbol" aria-hidden="true">✳</span><button class="card-play" type="button" data-song-id="${song.id}" aria-label="Play ${escapeHtml(song.title)}">▶</button></div>`;
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (character) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  })[character]);
}

function renderSongs(target, list) {
  target.innerHTML = list.map((song, index) => `
    <article class="song-card">
      ${coverMarkup(song, index)}
      <div class="song-meta"><strong title="${escapeHtml(song.title)}">${escapeHtml(song.title)}</strong><span class="song-duration">${escapeHtml(song.duration)}</span></div>
      <span class="song-artist">${escapeHtml(song.artist)}</span>
    </article>`).join("");
}

function renderArtists(artists) {
  artistList.innerHTML = artists.map((artist, index) => {
    const initials = artist.split(/\s+/).map((word) => word[0]).slice(0, 2).join("");
    const palette = palettes[(index + 2) % palettes.length];
    const count = songs.filter((song) => song.artist === artist).length;
    return `<div class="artist-item"><div class="artist-avatar" style="background:linear-gradient(135deg,${palette[0]},${palette[1]})">${escapeHtml(initials)}</div><div><strong>${escapeHtml(artist)}</strong><span>${count} ${count === 1 ? "track" : "tracks"}</span></div></div>`;
  }).join("");
}

function displayNotice(message) {
  audioNotice.textContent = message;
  audioNotice.classList.add("visible");
  clearTimeout(noticeTimeout);
  noticeTimeout = setTimeout(() => audioNotice.classList.remove("visible"), 4500);
}

function formatTime(seconds) {
  if (!Number.isFinite(seconds)) return "0:00";
  const minutes = Math.floor(seconds / 60);
  return `${minutes}:${String(Math.floor(seconds % 60)).padStart(2, "0")}`;
}

function selectSong(songId) {
  currentIndex = songs.findIndex((song) => song.id === Number(songId));
  if (currentIndex < 0) return;
  const song = songs[currentIndex];
  document.querySelector("#current-title").textContent = song.title;
  document.querySelector("#current-artist").textContent = song.artist;
  document.querySelector("#total-time").textContent = song.duration.replace(/^0/, "");
  document.querySelector("#player-art").style.background = `linear-gradient(135deg,${palettes[currentIndex % palettes.length].join(",")})`;
  audio.src = song.audio_url;
  audio.load();
  audio.play().then(() => {
    playButton.textContent = "Ⅱ";
    playButton.setAttribute("aria-label", "Pause");
  }).catch(() => {
    playButton.textContent = "▶";
    playButton.setAttribute("aria-label", "Play");
    displayNotice("Demo audio not available. Add demo MP3 files to backend/audio/ to enable playback.");
  });
}

document.addEventListener("click", (event) => {
  const playControl = event.target.closest("[data-song-id]");
  if (playControl) selectSong(playControl.dataset.songId);
});

playButton.addEventListener("click", () => {
  if (currentIndex < 0) {
    if (songs.length) selectSong(songs[0].id);
    return;
  }
  if (audio.paused) {
    audio.play().then(() => {
      playButton.textContent = "Ⅱ";
      playButton.setAttribute("aria-label", "Pause");
    }).catch(() => displayNotice("Demo audio not available. Add demo MP3 files to backend/audio/ to enable playback."));
  } else {
    audio.pause();
    playButton.textContent = "▶";
    playButton.setAttribute("aria-label", "Play");
  }
});

document.querySelector("#next-button").addEventListener("click", () => {
  if (songs.length) selectSong(songs[(currentIndex + 1 + songs.length) % songs.length].id);
});
document.querySelector("#previous-button").addEventListener("click", () => {
  if (songs.length) selectSong(songs[(currentIndex - 1 + songs.length) % songs.length].id);
});
document.querySelector("#like-button").addEventListener("click", (event) => {
  const button = event.currentTarget;
  const liked = button.textContent === "♥";
  button.textContent = liked ? "♡" : "♥";
  button.style.color = liked ? "" : "#f1a0a8";
});

audio.addEventListener("error", () => {
  playButton.textContent = "▶";
  playButton.setAttribute("aria-label", "Play");
  displayNotice("Demo audio not available. Add demo MP3 files to backend/audio/ to enable playback.");
});
audio.addEventListener("timeupdate", () => {
  document.querySelector("#elapsed-time").textContent = formatTime(audio.currentTime);
  if (Number.isFinite(audio.duration) && audio.duration > 0) {
    progress.value = String((audio.currentTime / audio.duration) * 100);
  }
});
audio.addEventListener("ended", () => {
  if (songs.length) selectSong(songs[(currentIndex + 1) % songs.length].id);
});
progress.addEventListener("input", () => {
  if (Number.isFinite(audio.duration) && audio.duration > 0) audio.currentTime = (Number(progress.value) / 100) * audio.duration;
});
document.querySelector("#volume").addEventListener("input", (event) => {
  audio.volume = Number(event.target.value);
});
audio.volume = 0.72;

let searchRequest;
searchInput.addEventListener("input", () => {
  clearTimeout(searchRequest);
  const query = searchInput.value.trim();
  if (!query) {
    searchResults.classList.add("hidden");
    return;
  }
  searchRequest = setTimeout(async () => {
    try {
      const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
      if (!response.ok) throw new Error(`Search failed (${response.status})`);
      const results = await response.json();
      renderSongs(searchGrid, results);
      searchEmpty.classList.toggle("hidden", results.length > 0);
      searchResults.classList.remove("hidden");
    } catch (error) {
      displayNotice("Unable to search right now. Check that the local server is running.");
      console.error(error);
    }
  }, 160);
});

document.addEventListener("keydown", (event) => {
  if (event.key === "/" && !["INPUT", "TEXTAREA"].includes(document.activeElement.tagName)) {
    event.preventDefault();
    searchInput.focus();
  }
  if (event.key === "Escape" && document.activeElement === searchInput) {
    searchInput.value = "";
    searchResults.classList.add("hidden");
    searchInput.blur();
  }
});

async function initialize() {
  try {
    const [songsResponse, artistsResponse] = await Promise.all([
      fetch("/api/songs"),
      fetch("/api/artists"),
    ]);
    if (!songsResponse.ok || !artistsResponse.ok) throw new Error("Could not load MusicStream catalogue.");
    songs = await songsResponse.json();
    const artists = await artistsResponse.json();
    renderSongs(trendingGrid, songs.slice(0, 8));
    renderArtists(artists);
  } catch (error) {
    trendingGrid.innerHTML = `<p class="empty-state">Music catalogue could not be loaded. Please refresh the page.</p>`;
    console.error(error);
  }
}

initialize();
