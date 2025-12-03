import json
import re
import requests
from datetime import datetime
from utils.output_s3 import store_grant_and_linking

def clean_award_id(award_id: str) -> list[str] | None:
    text = str(award_id).strip()

    # Find all digit sequences in the string
    digit_groups = re.findall(r'\d+', text)

    if not digit_groups:
        return None

    # If the string contains more than one award code (detected by prefix letters)
    # Example: "DMR-1809762 CBET-1916877"
    codes = re.findall(r'[A-Za-z]+[- ]*\d+', text)
    if len(codes) > 1:
        # Multiple award codes → return each full ID separately
        return [re.findall(r'\d+', code)[0] for code in codes]

    # Otherwise: one award code → combine digit pieces
    return ["".join(digit_groups)]


def get_award_from_NSF(award_id: str) -> str:
    #normalize the award_id to ensure it is a string
    normalized_award_id = clean_award_id(award_id)[0]
   
    url = f"http://api.nsf.gov/services/v1/awards/{normalized_award_id}.json"

    response = requests.get(url)
    data = response.json()

    amount = None
    startDate = None
    endDate = None
    principal_investigator = None
    grant_url = None
    title = None
    funderCode = "41___NATIONAL_SCIENCE_FOUNDATION_(ALEXANDRIA)"
    status = "ACTIVE"

    if response.status_code == 200 and data.get("response", {}).get("metadata", {}).get("totalCount", 0) > 0:
        # Access the first award in the list
        award = data["response"]["award"][0]
        amount = award.get("fundsObligatedAmt")

        project_start = award.get("startDate")
        if project_start:
            startDate = datetime.strptime(project_start, "%m/%d/%Y").strftime("%Y-%m-%d")

        project_end = award.get("expDate")
        if project_end:
            endDate = datetime.strptime(project_end, "%m/%d/%Y").strftime("%Y-%m-%d")
            end_date = datetime.strptime(project_end, "%m/%d/%Y").date()
            if end_date < datetime.now().date():
                status = "HISTORY"
        
        title = award.get("title")
        award_id = award.get("id")
        grant_url = "https://www.nsf.gov/awardsearch/show-award?AWD_ID=" + award_id

    result = f"""<grant>
    <grantId>{award_id}</grantId>
    <grantName>{title}</grantName>
    <funderCode>{funderCode}</funderCode>
    <amount>{amount}</amount>
    <startDate>{startDate}</startDate>
    <endDate>{endDate}</endDate>
    <grantURL>{grant_url}</grantURL>
    <profileVisibility>true</profileVisibility>
    <status>{status}</status>
</grant>"""
        
    return result


def lambda_handler(event, context):

    responses = {
        "grants": [],
        "linking": [],
        "errors": []
    }

    for record in event["Records"]:
        try:
            task = json.loads(record["body"])
            award_id = task.get("award_id")
            doi = task.get("doi")

            if not award_id:
                responses["errors"].append("Missing award_id")
                continue

            # list of extracted IDs, e.g. ["1748958", "1809762"]
            normalized_ids = clean_award_id(award_id)

            # Process each NSF award ID
            for nid in normalized_ids:
                grant_result = get_award_from_NSF(nid)
              
                # Store grant and linking info in S3
                stored = store_grant_and_linking(
                    funder_name="National Science Foundation",
                    doi=doi,
                    grant_result=grant_result,
                )

                responses["grants"].append(stored["grant_result"])
                responses["linking"].append(stored["grant_assets"])

        except Exception as e:
            responses["errors"].append(str(e))

    return {
        "statusCode": 200,
        "body": json.dumps(responses)
    }