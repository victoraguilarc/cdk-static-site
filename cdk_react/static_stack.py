from aws_cdk import core
from aws_cdk import (
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_certificatemanager as certificate_manager,
)

from config import StackConfig


class StaticSiteStack(core.Stack):
    """
    Docs for HTTPS: https://dev.to/miensol/https-on-cloudfront-using-certificate-manager-and-aws-cdk-3m50
    """

    def __init__(
        self,
        scope: core.Construct,
        construct_id: str,
        config: StackConfig,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.project_name = construct_id
        self.config = config

        self.s3_bucket = self.setup_s3_bucket()
        self.certificate = self.fetch_certificate()

        # CfnOutput(scope=scope, )
        self.setup_cloudfront()

    def setup_s3_bucket(self) -> s3.Bucket:
        return s3.Bucket(
            self,
            f'{self.project_name}-bucket',
            bucket_name=f'{self.project_name}-bucket',
            website_index_document='index.html',
            website_error_document='index.html',
            versioned=True,
        )

    def setup_cloudfront(self) -> cloudfront.CloudFrontWebDistribution:

        cloudfront_oai = cloudfront.OriginAccessIdentity(
            self,
            f'{self.project_name}-oai',
            comment=f'OAI for {self.project_name} website'
        )
        return cloudfront.CloudFrontWebDistribution(
            self,
            f'{self.project_name}-cloudfront',
            origin_configs=[
                cloudfront.SourceConfiguration(
                    s3_origin_source=cloudfront.S3OriginConfig(
                        s3_bucket_source=self.s3_bucket,
                        origin_access_identity=cloudfront_oai
                    ),
                    behaviors=[
                        cloudfront.Behavior(is_default_behavior=True)
                    ]
                )
            ],
            viewer_certificate=cloudfront.ViewerCertificate.from_acm_certificate(
                certificate=self.certificate,
                ssl_method=cloudfront.SSLMethod.SNI,
                aliases=[self.config.domain]
            ),
            error_configurations=[
                cloudfront.CfnDistribution.CustomErrorResponseProperty(
                    error_code=404,
                    error_caching_min_ttl=300,
                    response_code=200,
                    response_page_path='/index.html'
                )
            ]
        )

    def fetch_certificate(self) -> certificate_manager.Certificate:
        certificate_arn = self.format_arn(
            service='acm',
            resource='certificate',
            resource_name=self.config.cert_key,
        )
        return certificate_manager.Certificate.from_certificate_arn(
            scope=self,
            id=f'{self.project_name}-certificate',
            certificate_arn=certificate_arn,
        )

