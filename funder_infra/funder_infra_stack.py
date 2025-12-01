from aws_cdk import (
    aws_lambda as _lambda,
    Stack,
    aws_s3 as s3
)
from constructs import Construct
from funder_infra.import_pipline import import_existing_funder

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

        # --- Import existing NIH funder pipeline ---
        import_existing_funder(
            self,
            name="NIH",
            queue_arn="arn:aws:sqs:us-east-2:050752631001:NIH-Queue",
            lambda_arn="arn:aws:lambda:us-east-2:050752631001:function:NIH-Handler",
            asset_grant_linking_bucket=asset_grant_linking_bucket,
            brandeis_grants_bucket=brandeis_grants_bucket,
        )

        # Create the requests layer
        requests_layer = _lambda.LayerVersion(
            self,
            "RequestsLayer",
            code=_lambda.Code.from_asset("funder_infra/lambda/layers/requests_layer"),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_11],
        )

        # --- NEW FUNDERS BELOW ---
        # Funder NS
        # ns_queue = sqs.Queue(self, "FunderNSQueue")

        # ns_lambda = _lambda.Function(
        #     self,
        #     "FunderNSLambda",
        #     runtime=_lambda.Runtime.PYTHON_3_11,
        #     handler="handler.handler",
        #     code=_lambda.Code.from_asset("funder_infra/lambda/funder_ns"),
        # )

        # ns_lambda.add_event_source(lambda_event_sources.SqsEventSource(ns_queue))
        # bucket.grant_write(ns_lambda)
