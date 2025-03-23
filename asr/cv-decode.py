import os
import pandas as pd
import requests
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

# Path configuration – adjust these as needed
DATA_FOLDER = "data"  # Folder containing the data files
CSV_PATH = os.path.join(DATA_FOLDER, "cv-valid-dev.csv")
AUDIO_FOLDER = os.path.join(DATA_FOLDER, "cv-valid-dev")  # Folder containing the 4076 mp3 files
ASR_API_URL = "http://localhost:8001/asr"

# Setup logging configuration
logging.basicConfig(level=logging.INFO,  # Adjust to DEBUG for more detailed logs
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(), logging.FileHandler(os.path.join(DATA_FOLDER, "transcription_process.log"))])

# Create logger
logger = logging.getLogger(__name__)

# Read the CSV file
df = pd.read_csv(CSV_PATH)

generated_texts = []

# Function to process each file
def process_file(row):
    file_name = row['filename']
    file_path = os.path.join(AUDIO_FOLDER, file_name)
    
    if not os.path.exists(file_path):
        generated_texts.append(("FILE_NOT_FOUND", file_name))
        logger.warning(f"File not found: {file_path}")
        return
    
    try:
        with open(file_path, "rb") as f:
            files = {"file": (file_name, f, "audio/mpeg")}
            response = requests.post(ASR_API_URL, files=files)
            if response.status_code == 200:
                data = response.json()
                transcription = data.get("transcription", "")
                generated_texts.append((transcription, file_name))
                logger.info(f"Successfully transcribed {file_name}")
            else:
                generated_texts.append(("ERROR", file_name))
                logger.error(f"Error transcribing {file_name}: {response.status_code} - {response.text}")
    except Exception as e:
        generated_texts.append(("EXCEPTION", file_name))
        logger.error(f"Exception processing file {file_name}: {e}")

# Create ThreadPoolExecutor to handle multiple requests concurrently
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(process_file, row) for index, row in df.iterrows()]
    
    # Wait for all futures to complete
    for future in as_completed(futures):
        pass  # All exceptions and logging are already handled inside the process_file function

# Map the generated transcriptions back to the dataframe
df["generated_text"] = [text for text, _ in generated_texts]

# Save the updated CSV into the 'data' folder
output_csv_path = os.path.join(DATA_FOLDER, "cv-valid-dev-updated.csv")
df.to_csv(output_csv_path, index=False)
logger.info(f"Updated CSV saved to {output_csv_path}")
