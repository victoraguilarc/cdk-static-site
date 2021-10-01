from aws_cdk import (
    aws_ec2 as ec2,
    core,
)


class VPCStack(core.Stack):
    vpc_name: str = None
    vpc: ec2.IVpc = None

    def __init__(self, scope: core.Construct, id: str, vpc_name: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.vpc_name = vpc_name
        self.vpc = self.setup_vpc()

    def setup_vpc(self: core.Construct, vpc_name: str):
        return ec2.Vpc(
            self,
            vpc_name,
            max_azs=2,
            cidr='10.10.0.0/16',
            # configuration will create 3 groups in 2 AZs = 6 subnets.
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    subnet_type=ec2.SubnetType.PUBLIC,
                    name='Public',
                    cidr_mask=23  # 512 ip addresses
                ), ec2.SubnetConfiguration(
                    subnet_type=ec2.SubnetType.PRIVATE,
                    name='Private',
                    cidr_mask=23  # 512 ip addresses
                ), ec2.SubnetConfiguration(
                    subnet_type=ec2.SubnetType.ISOLATED,
                    name='Isolated',
                    cidr_mask=24  # 256 ip addresses
                )
            ],
            nat_gateways=1,
        )

    def get_vpc(self):
        return self.vpc
