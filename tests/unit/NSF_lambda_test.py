import sys, os

os.environ["GRANT_BUCKET"] = "brandeis-grants"
os.environ["LINKING_BUCKET"] = "asset-grant-linking"

# Project root
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.insert(0, ROOT)

# Lambda layer path (where utils/ lives)
LAYER_PATH = os.path.abspath(
    os.path.join(ROOT, "funder_infra/lambdas/layers/shared_utils_layer/python")
)
sys.path.insert(0, LAYER_PATH)

import json
from unittest.mock import patch

# Import AFTER sys.path and env vars set
from funder_infra.lambdas.NSF.handler import lambda_handler


# ----------------------------
# Fake event
# ----------------------------
fake_event = {
    "Records": [
        {
            "body": json.dumps({
                "award_id": "DMR-1809762 CBET-1916877 CMMT-2026834 BSF- 2016188",
                "doi": "10.1063/5.0202872"
            })
        }
    ]
}


# ----------------------------
# Patch CORRECT path
# ----------------------------
@patch("utils.output_s3.s3.put_object")
def test_lambda(mock_put_object):

    mock_put_object.return_value = {
        "ResponseMetadata": {"HTTPStatusCode": 200}
    }

    result = lambda_handler(fake_event, None)
    parsed_body = json.loads(result["body"])

    print("\n=== Lambda Output ===\n")
    print(parsed_body["grants"][0])
    

    print("\n=== S3 put_object calls ===\n")
    print("Number of S3 Call:", mock_put_object.call_count,"\n")

    for i, call in enumerate(mock_put_object.call_args_list, start=1):
        print(f"\n--- S3 Call #{i} ---")

        bucket = call.kwargs["Bucket"]
        key = call.kwargs["Key"]
        body = call.kwargs["Body"]
        content_type = call.kwargs.get("ContentType")

        print(f"Bucket:       {bucket}")
        print(f"Key:          {key}")
        print(f"Content-Type: {content_type}")

        print("\nBody:")
        print(body)  # raw body, real newlines
        print("\n=====================\n")


if __name__ == "__main__":
    test_lambda()
