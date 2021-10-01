import json
import environ
from dataclasses import dataclass
from typing import List

env = environ.Env()

AWS_ACCOUNT_ID = env.str('AWS_ACCOUNT_ID')
AWS_DEFAULT_REGION = env.str('AWS_DEFAULT_REGION')


@dataclass
class StackConfig(object):
    label: str
    stage: str
    domain: str
    cert_key: str

    @classmethod
    def get_configs(cls, config_file='./cdk.stacks.json') -> List['StackConfig']:
        config = open(config_file, 'r')
        config_json = json.load(config)

        stack_configs = []
        for item in config_json:
            stack_configs.append(StackConfig(**item))

        return stack_configs
