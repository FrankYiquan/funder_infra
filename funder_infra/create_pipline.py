from aws_cdk import (
    Duration,
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
    # create DLQ
    dlq = sqs.Queue(self, f"{name}-DLQ")

    # create SQS
    queue = sqs.Queue(
        self,
        f"{name}Queue",
        queue_name=f"{name}-Queue",
        retention_period=Duration.minutes(30),
        visibility_timeout=Duration.seconds(45),  # MUST be > Lambda timeout(30s)
        dead_letter_queue=sqs.DeadLetterQueue(
            max_receive_count=2,
            queue=dlq
        )
    )
   
    # Lambda code path based on funder name
    lambda_fn = _lambda.Function(
        self,
        f"{name}Lambda",
        runtime=_lambda.Runtime.PYTHON_3_11,
        handler="handler.lambda_handler", # what file to invoke (fileName.functionName)
        code=_lambda.Code.from_asset(f"funder_infra/lambdas/{name.lower()}"),
        layers=shared_layer,
        environment={
            "GRANT_BUCKET": brandeis_grants_bucket.bucket_name,
            "LINKING_BUCKET": asset_grant_linking_bucket.bucket_name,
        },
        function_name=f"{name}-Lambda",
        timeout=Duration.seconds(30),
    )

    # wire SQS trigger
    lambda_fn.add_event_source(
        lambda_event_sources.SqsEventSource(
            queue,
            batch_size=1,
        )
    )

    # give Lambda write access to bucket
    asset_grant_linking_bucket.grant_write(lambda_fn)
    brandeis_grants_bucket.grant_write(lambda_fn)

    return queue, lambda_fn
