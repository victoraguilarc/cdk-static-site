from typing import Any

from aws_cdk import core
from aws_cdk import (
    aws_certificatemanager as certificate_manager,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecr as ecr,
    aws_logs as logs,
    aws_iam as iam,
    aws_elasticloadbalancingv2 as elbv2,
)

from config import StackConfig


class SSRSiteStack(core.Stack):
    """
    Docs for HTTPS: https://dev.to/miensol/https-on-cloudfront-using-certificate-manager-and-aws-cdk-3m50
    """
    domain = None

    def __init__(
        self,
        scope: core.Construct,
        construct_id: str,
        vpc: Any,
        config: StackConfig,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.project_name = id
        self.config = config
        # self.vpc = self.setup_vpc()
        self.vpc = vpc

        self.certificate = self.setup_certificate()
        self.policy = self.setup_policy()
        self.log_group = self.setup_log_group()
        self.ecr_repo = self.setup_ecr_repository()
        self.ecs_cluster = self.setup_ecs_cluster()
        self.task_definition = self.setup_task_definition()
        self.ecs_service = self.setup_ecs_service()
        self.load_balancer = self.create_load_balancer()

        self.setup_balancer()

    def setup_vpc(self):
        return ec2.Vpc(self, f'{self.stack_name}-vpc', max_azs=2)

    def setup_log_group(self):
        return logs.LogGroup(
            self, f'{self.stack_name}-log-group',
            retention=logs.RetentionDays.ONE_WEEK,
            log_group_name=f'{self.stack_name}-log-group',
        )

    def setup_policy(self):
        policy = iam.Policy(self, f'{self.stack_name}-policy', policy_name=f'{self.stack_name}-policy')
        policy.add_statements(
            iam.PolicyStatement(
                resources=['*'],
                actions=['ecs:ListClusters', 'ecs:ListContainerInstances', 'ecs:DescribeContainerInstances']
            )
        )
        return policy

    def setup_ecr_repository(self):
        ecr_repo = ecr.Repository(
            self, f'{self.stack_name}-ecr',
            lifecycle_rules=[ecr.LifecycleRule(max_image_age=core.Duration.days(30))],
            removal_policy=core.RemovalPolicy.DESTROY,
            repository_name=self.stack_name,
        )
        core.CfnOutput(
            scope=self,
            id='ecr-repository',
            value=ecr_repo.repository_uri,
        )
        return ecr_repo

    def setup_ecs_cluster(self):
        return ecs.Cluster(
            self, f'{self.stack_name}-cluster',
            cluster_name=self.stack_name,
            vpc=self.vpc,
            container_insights=True,
        )

    def setup_task_definition(self, command=None):
        task_definition = ecs.FargateTaskDefinition(
            self, f'{self.stack_name}-tassk-definition',
            cpu=512,
            memory_limit_mib=1024,
            family=f'{self.stack_name}',
        )

        container_props = dict()
        if command:
            container_props['command'] = command

        app_container = task_definition.add_container(
            f'{self.stack_name}-container',
            image=ecs.ContainerImage.from_ecr_repository(self.ecr_repo),
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix=self.stack_name,
                log_group=self.log_group,
            ),
            environment={},
            **container_props,
        )
        app_container.add_port_mappings(ecs.PortMapping(container_port=3000))
        task_definition.task_role.attach_inline_policy(self.policy)
        return task_definition

    def setup_ecs_service(self, has_health_check=False):
        service_props = dict()
        if has_health_check:
            service_props['health_check_grace_period'] = core.Duration.seconds(10)

        service = ecs.FargateService(
            self, f'{self.stack_name}-service',
            service_name=self.stack_name,
            cluster=self.ecs_cluster,
            task_definition=self.task_definition,
            assign_public_ip=False,
            desired_count=1,
            max_healthy_percent=200,  # it makes zero downtime deployment
            min_healthy_percent=0,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE),
            **service_props,
        )
        scaling = service.auto_scale_task_count(
            min_capacity=1,
            max_capacity=10,
        )
        scaling.scale_on_cpu_utilization(
            f'{self.stack_name}-cpu-scaling',
            target_utilization_percent=50,
            scale_in_cooldown=core.Duration.seconds(60),
            scale_out_cooldown=core.Duration.seconds(60),
        )
        return service

    def setup_certificate(self) -> certificate_manager.Certificate:

        certificate = certificate_manager.Certificate(
            self,
            f'{self.project_name}-certificate',
            domain_name=self.domain,
            validation_method=certificate_manager.ValidationMethod.DNS,
        )
        return certificate

    def create_load_balancer(self):
        return elbv2.ApplicationLoadBalancer(
            self, f'{self.stack_name}-load-balancer',
            vpc=self.vpc,
            deletion_protection=False,
            http2_enabled=True,
            idle_timeout=core.Duration.seconds(60),
            internet_facing=True,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PUBLIC,
            ),
        )

    def setup_balancer(self):
        # Redirection 80 --> 443
        redirect_listener = self.load_balancer.add_listener('redirect', port=80, open=True)
        redirect_listener.add_redirect_response(
            'redirect',
            status_code='HTTP_301',
            protocol='HTTPS',
            port='443',
        )

        # Listener: 443
        https_listener = self.load_balancer.add_listener(
            f'{self.stack_name}-listener',
            port=443,
            certificates=[self.certificate],
            open=True
        )
        https_listener.add_targets(
            f'{self.stack_name}-target', port=80,
            deregistration_delay=core.Duration.seconds(30),
            slow_start=core.Duration.seconds(30),
            targets=[self.ecs_service],
            health_check=elbv2.HealthCheck(path='/')
        )
        return self.load_balancer

