import os
import json
import uuid
from datetime import datetime
import boto3
import re

s3 = boto3.client("s3")

GRANT_BUCKET_NAME = os.environ["GRANT_BUCKET"]
LINKING_BUCKET_NAME = os.environ["LINKING_BUCKET"]

def store_grant_and_linking(funder_name: str, doi: str, grant_result:str) -> dict:
    """Store grant XML and linking JSON in S3.
    """

    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S")

    safe_funder = funder_name.replace(" ", "_").lower()
    short_id = uuid.uuid4().hex[:6]

    match = re.search(r"<grantId>(.*?)</grantId>", grant_result)
    award_id = match.group(1) if match else None


    # --- Grant XML ---
    filename = f"{safe_funder}/{award_id}_{timestamp}_{short_id}.xml"
    s3.put_object(
        Bucket=GRANT_BUCKET_NAME,
        Key=filename,
        Body=grant_result,
        ContentType="application/xml"
    )

    # --- Linking JSON ---
    asset_grant = {
        "doi": doi,
        "awardnumbers": award_id,  
    }

    normalized_doi = doi.replace("/", "_")
    linking_filename = f"{normalized_doi}/{award_id}_{timestamp}.json"

    s3.put_object(
        Bucket=LINKING_BUCKET_NAME,
        Key=linking_filename,
        Body=json.dumps(asset_grant),
        ContentType="application/json"
    )

    return {
        "grant_result": grant_result,
        "grant_assets": asset_grant
    }
