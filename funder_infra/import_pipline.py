from aws_cdk import (
    aws_s3 as s3,
    aws_sqs as sqs,
    aws_lambda as _lambda,
    aws_lambda_event_sources as lambda_event_sources,
)

def import_existing_funder(
    self,
    name: str,
    queue_arn: str,
    lambda_arn: str,
    asset_grant_linking_bucket: s3.IBucket, 
    brandeis_grants_bucket: s3.IBucket, 
) -> tuple[sqs.Queue, _lambda.Function]:
    """
    Imports existing SQS + Lambda for an existing funder,
    reconnects event source, and grants S3 write permissions.
    """
    # import SQS
    queue = sqs.Queue.from_queue_arn(
        self,
        f"{name}Queue",
        queue_arn
    )

    # import Lambda
    lambda_fn = _lambda.Function.from_function_arn(
        self,
        f"{name}Lambda",
        lambda_arn
    )

    # reconnect SQS → Lambda trigger
    lambda_fn.add_event_source(
        lambda_event_sources.SqsEventSource(queue)
    )

    # grant bucket write perms
    asset_grant_linking_bucket.grant_write(lambda_fn)
    brandeis_grants_bucket.grant_write(lambda_fn)

    return queue, lambda_fn
