import os
import aws_cdk as cdk

from funder_infra.funder_infra_stack import FunderInfraStack

app = cdk.App()

FunderInfraStack(
    app,
    "FunderInfraStack",
    env=cdk.Environment(
        account=os.getenv("CDK_DEFAULT_ACCOUNT"),
        region="us-east-2"   # IMPORTANT: match your actual AWS region
    )
)

app.synth()