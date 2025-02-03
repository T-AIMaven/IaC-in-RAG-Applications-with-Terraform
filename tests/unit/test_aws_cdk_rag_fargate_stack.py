import aws_cdk as core
import aws_cdk.assertions as assertions
from aws_cdk_rag_fargate.aws_cdk_rag_fargate_stack import AwsCdkRagFargateStack

def test_fargate_service_created():
    app = core.App()
    stack = AwsCdkRagFargateStack(app, "aws-cdk-rag-fargate")
    template = assertions.Template.from_stack(stack)

    template.has_resource_properties("AWS::ECS::Service", {
        "LaunchType": "FARGATE"
    })

def test_task_definition_created():
    app = core.App()
    stack = AwsCdkRagFargateStack(app, "aws-cdk-rag-fargate")
    template = assertions.Template.from_stack(stack)

    template.has_resource_properties("AWS::ECS::TaskDefinition", {
        "RequiresCompatibilities": ["FARGATE"]
    })

def test_load_balancer_created():
    app = core.App()
    stack = AwsCdkRagFargateStack(app, "aws-cdk-rag-fargate")
    template = assertions.Template.from_stack(stack)

    template.has_resource_properties("AWS::ElasticLoadBalancingV2::LoadBalancer", {
        "Type": "application"
    })

def test_s3_bucket_created():
    app = core.App()
    stack = AwsCdkRagFargateStack(app, "aws-cdk-rag-fargate")
    template = assertions.Template.from_stack(stack)

    template.has_resource_properties("AWS::S3::Bucket", {
        "VersioningConfiguration": {
            "Status": "Enabled"
        }
    })

def test_outputs_created():
    app = core.App()
    stack = AwsCdkRagFargateStack(app, "aws-cdk-rag-fargate")
    template = assertions.Template.from_stack(stack)

    template.has_output("LoadBalancerDNS", {})
    template.has_output("DocumentBucketName", {})

def test_auto_scaling_policy_created():
    app = core.App()
    stack = AwsCdkRagFargateStack(app, "aws-cdk-rag-fargate")
    template = assertions.Template.from_stack(stack)

    template.has_resource_properties("AWS::ApplicationAutoScaling::ScalingPolicy", {
        "PolicyType": "TargetTrackingScaling"
    })