from aws_cdk import (
    aws_lambda as _lambda,
    Stack,
    aws_s3 as s3
)
from constructs import Construct
from funder_infra.import_pipline import import_existing_funder
from funder_infra.create_pipline import create_funder_pipeline

class FunderInfraStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # --- Import existing S3 ---
        asset_grant_linking_bucket = s3.Bucket.from_bucket_name(
            self, "asset-grant-linking", "asset-grant-linking"
        )

        brandeis_grants_bucket = s3.Bucket.from_bucket_name(
            self, "brandeis-grants", "brandeis-grants"
        )

        # # --- Import existing NIH funder pipeline ---
        # import_existing_funder(
        #     self,
        #     name="NIH",
        #     queue_arn="arn:aws:sqs:us-east-2:050752631001:NIH-Queue",
        #     lambda_arn="arn:aws:lambda:us-east-2:050752631001:function:NIH-Handler",
        #     asset_grant_linking_bucket=asset_grant_linking_bucket,
        #     brandeis_grants_bucket=brandeis_grants_bucket,
        # )

        # --- Import New Layers ---

        # Create the requests layer
        requests_layer = _lambda.LayerVersion(
            self,
            "RequestsLayer",
            code=_lambda.Code.from_asset("funder_infra/lambdas/layers/requests_layer"),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_11],
            layer_version_name="requests-layer"
        )

        helper_layer = _lambda.LayerVersion(
            self,
            "HelperLayer",
            code=_lambda.Code.from_asset("funder_infra/lambdas/layers/shared_utils_layer"),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_11],
            layer_version_name="helper-layer"
        )

        # --- NEW FUNDERS BELOW ---

        # Create NSF funder pipeline
        create_funder_pipeline(
            self,
            name="NSF",
            asset_grant_linking_bucket=asset_grant_linking_bucket,
            brandeis_grants_bucket=brandeis_grants_bucket,
            shared_layer=[requests_layer,helper_layer]
        )
        