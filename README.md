# HTX xData Technical Test

## Overview
This repository contains a hosted microservice for Automatic Speech Recognition (ASR) using Facebook's [wav2vec2-large-960h](https://huggingface.co/facebook/wav2vec2-large-960h). It also includes scripts for processing Mozilla’s Common Voice dataset and indexing data into an Elasticsearch backend with a Search UI frontend.

## Repository Structure
- **asr/**: Contains the ASR API (`asr_api.py`), Dockerfile for containerization, and `cv-decode.py` for batch transcription.
- **elastic-backend/**: Contains `docker-compose.yml` to set up a 2-node Elasticsearch cluster and `cv-index.py` to index transcriptions.
- **search-ui/**: Contains configuration and Docker Compose for the Search UI.
- **deployment-design/**: Contains the proposed deployment architecture (`design.pdf`).
- **essay.pdf**: Contains the 500-word essay on model monitoring and drift tracking.

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/myrepo.git
   cd myrepo
Install dependencies:

bash
Copy
Edit
pip install -r requirements.txt
Run the ASR microservice:

bash
Copy
Edit
cd asr
uvicorn asr_api:app --host 0.0.0.0 --port 8001
Verify the service with:

bash
Copy
Edit
curl http://localhost:8001/ping
Batch Process Common Voice files: Place your cv-valid-dev.csv and mp3 files in a folder (e.g., cv-valid-dev) then run:

bash
Copy
Edit
python cv-decode.py
Containerization:

ASR API Docker Image: Build using the Dockerfile in the asr/ directory.
bash
Copy
Edit
docker build -t asr-api .
Elasticsearch and Search UI: Use the provided docker-compose.yml files in elastic-backend/ and search-ui/.
Deployment: Follow the instructions in this README and in the deployment-design/design.pdf for deploying on Azure or AWS.




Troubleshooting code

can't install torch
pip install --upgrade pip setuptools wheel

Specific python version recommended for installation of torch module
