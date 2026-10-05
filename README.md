# MusicStream

MusicStream is a local-only fictional music streaming demo built for learning AWS DevOps concepts. It runs as one Flask application that serves the frontend and REST API. It creates no AWS resources and uses no AWS SDK.

## Architecture

- **Frontend:** responsive HTML, CSS, and vanilla JavaScript served by Flask.
- **Backend:** Flask REST API with CORS enabled. The API reads the fictional catalogue from `backend/data/songs.json`.
- **Audio:** twelve original, synthesized 30-second instrumental sketches in WAV format are served from `backend/audio/`.
- **Tests:** pytest tests exercise the API and homepage.

All included artist, album, and song names are fictional demo metadata. The cover artwork is generated with CSS and no third-party brand assets or copyrighted music are used.

## Requirements

- Python 3.9 or newer
- pip

## Installation

From this `musicstream` directory, create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
```

On macOS/Linux, activate with `source .venv/bin/activate` and use the same pip command with forward-slash paths.

## Run locally

From the project root:

```powershell
python run.py
```

The server listens on `0.0.0.0:8083`; open **http://localhost:8083**. The Flask homepage, frontend assets, API, and optional audio are served from the same process.

The bundled WAV sketches are generated specifically for this project and are not samples of existing commercial music. To regenerate them, run `python backend\generate_demo_audio.py` from the project root. You can also place your own audio files in `backend/audio/` and update the corresponding catalogue URLs.

## Run tests

```powershell
python -m pytest
```

## API endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/` | MusicStream homepage |
| GET | `/api/status` | JSON application status |
| GET | `/api/songs` | All songs |
| GET | `/api/songs/<id>` | One song, or JSON 404 |
| GET | `/api/search?q=<query>` | Search by title, artist, album, and genre; an empty query returns `[]` |
| GET | `/api/artists` | Unique artist names |
| GET | `/audio/<filename>` | Local demo audio file |

Unknown `/api/` routes return a JSON 404 response.

## Folder structure

```text
musicstream/
├── backend/
│   ├── app.py
│   ├── generate_demo_audio.py
│   ├── requirements.txt
│   ├── audio/
│   └── data/
│       └── songs.json
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── tests/
│   └── test_api.py
├── .gitignore
├── README.md
└── run.py
```

## Future AWS deployment architecture

This local dry run provisions no cloud infrastructure. A possible future learning deployment could package the Flask API in a container and run it on Amazon ECS with AWS Fargate behind an Application Load Balancer; store static frontend assets in Amazon S3 and serve them through Amazon CloudFront; store licensed audio in S3; and use Amazon RDS only if persistent user or playlist data is added. A CI/CD pipeline could build and test the app before publishing versioned artifacts and deploying to a separate AWS environment. Add IAM roles, secrets management, monitoring, and budget controls before any real deployment.
