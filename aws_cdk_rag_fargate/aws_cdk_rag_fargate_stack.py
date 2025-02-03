import os
import aws_cdk as cdk
from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecr as ecr,
    aws_ecs_patterns as ecs_patterns,
    aws_s3 as s3,
    aws_secretsmanager as secretsmanager,

)
from constructs import Construct

class AwsCdkRagFargateStack(Stack): 

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create a VPC
        vpc = ec2.Vpc(self, "RagVpc", max_azs=2)

        # Create an ECS cluster
        cluster = ecs.Cluster(self, "RagCluster", vpc=vpc)

        # Create an S3 bucket to store documents
        document_bucket = s3.Bucket(self, "RagDocumentBucket",
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED,
            removal_policy=cdk.RemovalPolicy.DESTROY  # Use RETAIN in production
        )
        

        # Retrieve the secret
        secret = secretsmanager.Secret.from_secret_name_v2(
            self, "RagAppSecrets", "rag-app"
        )

        # Create a Fargate service with an Application Load Balancer
        fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self, "RagFargateService",
            cluster=cluster,
            cpu=512,
            memory_limit_mib=1024,
            desired_count=1,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_asset("app"),
                container_port=8000,
                environment={
                    "DOCUMENT_BUCKET": document_bucket.bucket_name,
                },
                secrets={
                    "QDRANT_URL": ecs.Secret.from_secrets_manager(secret, "QDRANT_URL"),
                    "QDRANT_API_KEY": ecs.Secret.from_secrets_manager(secret, "QDRANT_API_KEY"),
                    "OPENAI_API_KEY": ecs.Secret.from_secrets_manager(secret, "OPENAI_API_KEY"),
                }
            ),
            public_load_balancer=True
        )

        # Add Auto Scaling
        scaling = fargate_service.service.auto_scale_task_count(
            min_capacity=1,
            max_capacity=3  # Adjust this value based on your needs
        )

        # Add CPU utilization scaling policy
        scaling.scale_on_cpu_utilization("CpuScaling",
            target_utilization_percent=70,
            scale_in_cooldown=cdk.Duration.seconds(60),
            scale_out_cooldown=cdk.Duration.seconds(60)
        )
        
        # Grant the task read and write access to the S3 bucket
        document_bucket.grant_read_write(fargate_service.task_definition.task_role)

        # Output the load balancer DNS
        cdk.CfnOutput(self, "LoadBalancerDNS",
            value=fargate_service.load_balancer.load_balancer_dns_name,
            description="Load Balancer DNS",
            export_name="RagLoadBalancerDNS"
        )

        # Output the S3 bucket name
        cdk.CfnOutput(self, "DocumentBucketName",
            value=document_bucket.bucket_name,
            description="Document Bucket Name",
            export_name="RagDocumentBucketName"
        )
