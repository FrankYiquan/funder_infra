import os
import json
import uuid
from datetime import datetime
import boto3
import re
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client("s3")

GRANT_BUCKET_NAME = os.environ["GRANT_BUCKET"]
LINKING_BUCKET_NAME = os.environ["LINKING_BUCKET"]

def store_grant_and_linking(funder_name: str, doi: str, grant_result: str) -> dict:
    """Store grant XML and linking JSON in S3, with detailed logging."""

    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    safe_funder = funder_name.replace(" ", "_").lower()
    short_id = uuid.uuid4().hex[:6]

    # Extract award ID from XML
    match = re.search(r"<grantId>(.*?)</grantId>", grant_result)
    award_id = match.group(1) if match else None

    # --------------------
    # Store Grant XML
    # --------------------
    grant_key = f"{safe_funder}/{award_id}_{timestamp}_{short_id}.xml"
    s3.put_object(
        Bucket=GRANT_BUCKET_NAME,
        Key=grant_key,
        Body=grant_result,
        ContentType="application/xml"
    )

    logger.info(json.dumps({
        "event": "Stored Grant XML",
        "bucket": GRANT_BUCKET_NAME,
        "key": grant_key,
        "award_id": award_id,
        "funder": funder_name,
        "xml_length": len(grant_result)
    }))

    # --------------------
    # Store Linking JSON
    # --------------------
    asset_grant = {
        "doi": doi,
        "awardnumbers": award_id,
    }

    normalized_doi = doi.replace("/", "_")
    linking_key = f"{normalized_doi}/{award_id}.json"

    linking_body = json.dumps(asset_grant)

    s3.put_object(
        Bucket=LINKING_BUCKET_NAME,
        Key=linking_key,
        Body=linking_body,
        ContentType="application/json"
    )

    logger.info(json.dumps({
        "event": "Stored Linking JSON",
        "bucket": LINKING_BUCKET_NAME,
        "key": linking_key,
        "award_id": award_id,
        "doi": doi,
        "json_length": len(linking_body)
    }))


    return {
        "grant_result": grant_result,
        "grant_assets": asset_grant,
        "grant_key": grant_key,
        "linking_key": linking_key
    }
