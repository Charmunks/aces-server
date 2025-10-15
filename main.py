from fastapi import FastAPI
import requests
import os
import logging
from fastapi.middleware.cors import CORSMiddleware
# -----------------------------------------------------------
# Logging configuration
# -----------------------------------------------------------
logging.basicConfig(
    level=logging.DEBUG,  # Use DEBUG for detailed logs
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger(__name__)

# -----------------------------------------------------------
# FastAPI setup
# -----------------------------------------------------------
app = FastAPI()

# Environment variables
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_ID = os.getenv("AIRTABLE_TABLE_ID")

if not all([AIRTABLE_API_KEY, AIRTABLE_BASE_ID, AIRTABLE_TABLE_ID]):
    logger.warning("⚠️ Missing one or more Airtable environment variables!")

# -----------------------------------------------------------
# API route
# -----------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Accept requests from any domain
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods: GET, POST, etc.
    allow_headers=["*"],  # Allow all headers
)

@app.get("/count")
def get_airtable_record_count():
    """
    Fetches and returns the total number of records in an Airtable table.
    Includes detailed debug logging.
    """
    logger.debug("Starting Airtable record count retrieval...")
    logger.debug(f"Base ID: {AIRTABLE_BASE_ID}")
    logger.debug(f"Table ID: {AIRTABLE_TABLE_ID}")

    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_ID}"
    headers = {"Authorization": f"Bearer {AIRTABLE_API_KEY}"}

    total_records = 0
    offset = None
    iteration = 0

    try:
        while True:
            iteration += 1
            params = {}
            if offset:
                params["offset"] = offset
                logger.debug(f"Iteration {iteration}: continuing from offset {offset}")
            else:
                logger.debug(f"Iteration {iteration}: fetching first page")

            response = requests.get(url, headers=headers, params=params)
            logger.debug(f"HTTP GET {response.url} -> {response.status_code}")

            if response.status_code != 200:
                logger.error(f"Airtable API request failed: {response.text}")
                return {
                    "error": f"Failed to fetch from Airtable (status {response.status_code})",
                    "details": response.text,
                }

            data = response.json()
            records = data.get("records", [])
            batch_count = len(records)
            total_records += batch_count

            logger.debug(f"Fetched {batch_count} records (running total: {total_records})")

            offset = data.get("offset")
            if not offset:
                logger.debug("No more pages left to fetch.")
                break

        logger.info(f"Finished: total record count = {total_records}")
        return {"table_id": AIRTABLE_TABLE_ID, "record_count": total_records}

    except Exception as e:
        logger.exception("An error occurred while fetching Airtable data.")
        return {"error": str(e)}
