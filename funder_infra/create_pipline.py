from aws_cdk import (
    aws_lambda as lambda_,
    aws_s3 as s3,
    aws_sqs as sqs,
    aws_lambda as _lambda,
    aws_lambda_event_sources as lambda_event_sources,
)
def create_funder_pipeline(
        self, name: str, 
        asset_grant_linking_bucket: s3.IBucket, 
        brandeis_grants_bucket: s3.IBucket, 
        shared_layer: list[lambda_.ILayerVersion]
    ) -> tuple[sqs.Queue, _lambda.Function]:
    """
    Creates:
    - 1 SQS queue
    - 1 Lambda
    - Event source mapping (SQS -> Lambda)
    - S3 write permissions
    """
    # create SQS
    queue = sqs.Queue(self, f"{name}Queue")

    # Lambda code path based on funder name
    lambda_fn = _lambda.Function(
        self,
        f"{name}Lambda",
        runtime=_lambda.Runtime.PYTHON_3_11,
        handler="handler.handler", # what file to invoke (fileName.functionName)
        code=_lambda.Code.from_asset(f"funder_infra/lambda/{name.lower()}"),
        layers=shared_layer,
    )

    # wire SQS trigger
    lambda_fn.add_event_source(
        lambda_event_sources.SqsEventSource(queue)
    )

    # give Lambda write access to bucket
    asset_grant_linking_bucket.grant_write(lambda_fn)
    brandeis_grants_bucket.grant_write(lambda_fn)

    return queue, lambda_fn
