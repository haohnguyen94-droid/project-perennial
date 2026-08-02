import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.client import Client
from src.utils.youtube_logger import create_logger
from pathlib import Path
import json
import os
import argparse
from dotenv import load_dotenv

load_dotenv()

def initialize_firestore(credentials_path: Path) -> Client:
    if not credentials_path.is_file():
        raise FileNotFoundError(
            f"Firebase credentials file not found: {credentials_path}"
        )

    if not firebase_admin._apps:
        firebase_credentials = credentials.Certificate(
            str(credentials_path)
        )
        firebase_admin.initialize_app(firebase_credentials)

    return firestore.client()

def load_json(path, default):
    """helper function to load json files"""

    #if filepath is bad return default
    if not os.path.exists(path):
        return default

    with open(path, "r", encoding="utf-8") as f:
        content = f.read().strip()

        #if json is empty return default
        if not content:
            return default
        
        return json.loads(content)

def upload_file(db: Client, file_path: Path, collection_name: str, logger) -> None:
    try:
        json_data = load_json(file_path, None) # dictionary of <video IDs>:<data objects>
        if json_data is None: raise FileNotFoundError
        if not json_data:
            logger.warning(f"{file_path}: contains no documents")
            return
        
        for key, value in json_data.items():
            document_id = key
            db.collection(collection_name).document(document_id).set(value)
            logger.info(f"Uploaded {file_path.name} to {collection_name}/{document_id}")

    except FileNotFoundError as e:
        logger.error(f"{file_path}: File not found")
    except Exception as e:
        logger.error(f"{file_path}: Error, {e}")

def main() -> None:
    parser = argparse.ArgumentParser(description="Upload YouTube transcripts to Google Firestore.")
    parser.add_argument("filepath", type=Path, help="Filepath with data to upload")
    parser.add_argument("collection",help="Collection to upload to")

    args = parser.parse_args()
    
    logger = create_logger("firestore.log")
    credentials_path = Path(os.getenv("FIRESTORE_CREDENTIALS"))

    try:
        db = initialize_firestore(credentials_path)
        upload_file(db, args.filepath, args.collection, logger)

    except (FileNotFoundError, NotADirectoryError, ValueError) as error:
        logger.error("%s", error)
        raise SystemExit(1) from error
    except Exception:
        logger.exception("Unexpected upload failure.")
        raise SystemExit(1)


if __name__ == "__main__":
    main()