.PHONY: docs coverage fixtures
.SILENT: clean

include .env
export

STACK=static-site-beta

synth:
	cdk synth $(STACK)

diff:
	cdk diff $(STACK)

deploy:
	cdk deploy $(STACK)

destroy:
	cdk destroy $(STACK)
