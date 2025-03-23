# HTX xData Technical Test

This repository contains a complete end-to-end solution for an Automatic Speech Recognition (ASR) application and its associated search functionality. The project consists of three main components:

- **ASR Microservice:** A FastAPI service that transcribes audio files using Facebook's wav2vec2-large-960h model.
- **Elastic Backend:** An Elasticsearch cluster for storing and indexing transcriptions, along with a script to load data from CSV.
- **Search UI:** A React/Next.js application using Elastic's Search UI for end users to search and filter transcriptions based on fields such as `generated_text`, `duration`, `age`, `gender`, and `accent`.

This README provides detailed instructions for local testing and AWS deployment using the AWS Free Tier.

---

## Table of Contents

- [Deployment](#deployment)
- [Prerequisites](#prerequisites)
- [Local Setup and Testing](#local-setup-and-testing)
  - [Set Up Environment](#set-up-environment)
  - [1. ASR Microservice](#1-asr-microservice)
  - [2. Elastic Backend](#2-elastic-backend)
  - [3. Search UI](#3-search-ui)
- [AWS Deployment](#aws-deployment)
  - [EC2 Setup (Amazon Linux)](#ec2-setup-amazon-linux)
  - [Deploying Elastic Backend](#deploying-elastic-backend)
  - [Deploying Search UI](#deploying-search-ui)
- [Security and Network Configuration](#security-and-network-configuration)
- [Additional Notes](#additional-notes)


---

## Deployment
URL:
http://ec2-54-255-189-192.ap-southeast-1.compute.amazonaws.com:3000/
---

## Prerequisites

- **Docker & Docker Compose:** Ensure Docker and Docker Compose are installed.
- **Python 3.8+** (for running the ASR microservice and elastic-backend scripts).
- **Node.js 14+** (for running the Search UI frontend).
- **AWS Account** (for deployment on the free tier, using EC2 and S3).

---

## Local Setup and Testing
### Set Up Environment
   ```
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
OR
```
chmod +x setup_env.sh
./setup_env.sh
source venv/bin/activate
```

### 1. ASR Microservice
1. **Environment Variables:**
Create a `.env` file in the `asr` folder. For example:
   ```
   MODEL_NAME=facebook/wav2vec2-large-960h
   ```
2. **Install Dependencies:** Optional as the main requirements.txt at root level has the same packages
   ```
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Run the Service:**
   ```
   cd asr
   uvicorn asr_api:app --host 0.0.0.0 --port 8001
   ```
4. **Test the API:**
   Visit: http://localhost:8001/ping

### 2. Elastic Backend
 
1. **Start Elasticsearch:**
Navigate to the elastic-backend folder and run:
   ```
   cd elastic-backend
   docker-compose up -d
   ```

2. **Copy Data:** Copy over output csv from asr folder

3. **Index Data:** Run the indexing script (ensure your CSV is available):
   ```
   python cv-index.py
   ```

4. **Verify Indexing:**
   ```
   curl -X GET "http://localhost:9200/cv-transcriptions/_search?pretty"
   ```

### 2. Search UI
1.**Install Dependencies:**
   ```
   cd search-ui
   npm install
   ```
2.**Configure Environment:**
In the Next.js app SearchUI.tsx, update the connection URL for Elasticsearch.

host="http://<BACKEND_EC2_PUBLIC_IP>:9200"
Replace <BACKEND_EC2_PUBLIC_IP> with the proper IP during AWS deployment. For local testing, you can use localhost.

3.**Build and Run:**
   ```
   npm run build
   docker-compose up -d
   ```
4.**Access the UI:**
- Open http://localhost:3000 in your browser.

## AWS Deployment
For AWS deployment (using the free tier), we assume separate EC2 instances for the Elastic Backend and the Search UI.

### EC2 Setup (Amazon Linux)
1. **Launch EC2 Instances:**
- Elastic Backend EC2: Use Amazon Linux 2, t2.medium due to higher requirements
- Search UI EC2: Use Amazon Linux 2, t2.micro.

2. **Security Groups:**
- Elastic Backend: Allow inbound on port 9200 (only from the Search UI instance or your IP).
- Search UI: Allow inbound on port 3000 (HTTP access) and SSH (port 22).

### Deploying Elastic Backend
1. **SSH into the Elastic Backend EC2 Instance:**
   ```
   ssh -i /path/to/your-key.pem ec2-user@<BACKEND_EC2_PUBLIC_IP>
   ```

2. **Install Docker & Docker Compose (using YUM):**
   ```
   sudo yum update -y
   sudo yum install -y docker
   sudo service docker start
   sudo systemctl enable docker
   sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   docker-compose --version
   ```
3. **Copy the elastic-backend Folder to EC2:**
   ```
   scp -i /path/to/your-key.pem -r ./elastic-backend ec2-user@<BACKEND_EC2_PUBLIC_IP>:/home/ec2-user/
   ```

4. **Run Elasticsearch:**
   ```
   cd /home/ec2-user/elastic-backend
   docker-compose up -d
   ```
5. **Run the Indexing Script:**
   ```
   python3 cv-index.py
   ```

### Deploying Search UI
1. **SSH into the Search UI EC2 Instance:**
   ```
   ssh -i /path/to/your-key.pem ec2-user@<SEARCH_UI_EC2_PUBLIC_IP>
   ```
2. **Install Docker & Docker Compose (similar to above):**
   ```
   sudo yum update -y
   sudo yum install -y docker
   sudo service docker start
   sudo systemctl enable docker
   sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   docker-compose --version
   ```
3. **Copy the search-ui Folder to EC2:**
   ```
   scp -i /path/to/your-key.pem -r ./search-ui ec2-user@<SEARCH_UI_EC2_PUBLIC_IP>:/home/ec2-user/
   ```

4. **Update the Frontend Configuration:**
Ensure that the variable (or hard-coded URL) in your frontend points to:
   ```
   http://<BACKEND_EC2_PUBLIC_IP>:9200
   ```
5. **Run the Search UI Container:**
   ```
   cd /home/ec2-user/search-ui
   docker-compose up -d
   ```

6. **Access the Search UI:**
Open a browser and visit: http://<SEARCH_UI_EC2_PUBLIC_IP>:3000

## Security and Network Configuration
- VPC: Both EC2 instances should be within the same VPC to allow secure communication using private IP addresses (if desired). For simplicity, use public IP addresses but restrict access using Security Groups.

- Security Groups:   
   - Elastic Backend: Allow inbound on port 9200 from the Search UI instance’s IP or from within the VPC.

   - Search UI: Allow inbound on port 3000 from the Internet.

- DNS: AWS provides a public DNS name for each EC2 instance. You can use these or configure your own domain via Route 53 if needed.

## Additional Notes
- CSV Storage: It is recommended to store cv-valid-dev.csv on S3 for persistence and update cv-index.py to load from the S3 URL instead. However, to avoid discrepency in the code in asr - did not implement s3 upload.

- Logs & Monitoring: Monitor Docker logs using docker logs <container_name> and consider setting up CloudWatch on AWS for production-level monitoring.

- Scaling: This setup is designed for a minimal free-tier deployment. For higher loads or production, consider adding load balancers, auto-scaling, or managed services. Considered EKS kubernetes, however for this small scale, ec2 was sufficient

