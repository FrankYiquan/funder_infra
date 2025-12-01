import aws_cdk as core
import aws_cdk.assertions as assertions

from funder_infra.funder_infra_stack import FunderInfraStack

# example tests. To run these tests, uncomment this file along with the example
# resource in funder_infra/funder_infra_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = FunderInfraStack(app, "funder-infra")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
