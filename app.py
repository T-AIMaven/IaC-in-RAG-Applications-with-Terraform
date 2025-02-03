#!/usr/bin/env python3
import os

import aws_cdk as cdk

from aws_cdk_rag_fargate.aws_cdk_rag_fargate_stack import AwsCdkRagFargateStack


app = cdk.App()
AwsCdkRagFargateStack(app, "AwsCdkRagFargateStack")

app.synth()
