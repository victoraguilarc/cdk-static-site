#!/usr/bin/env python3
import os

from aws_cdk import core as cdk

# For consistency with TypeScript code, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.
from aws_cdk import core

from cdk_react.cdk_react_stack import CdkReactStack
from common_stack import VPCStack
from config import AWS_ACCOUNT_ID, AWS_DEFAULT_REGION, StackConfig
from ssr_stack import SSRSiteStack
from static_stack import StaticSiteStack


def synth():
    app = core.App()
    aws_account = core.Environment(
        account=AWS_ACCOUNT_ID,
        region=AWS_DEFAULT_REGION,
    )

    # vpc_stack = VPCStack(
    #     scope=app,
    #     id=f'{config.stage}-vpc',
    #     vpc_name=config.stage,
    #     env=aws_account,
    # )

    for config in StackConfig.get_configs():
        StaticSiteStack(
            scope=app,
            construct_id=config.label,
            config=config,
            env=aws_account,
        )
        # SSRSiteStack(app)

    app.synth()


synth()
