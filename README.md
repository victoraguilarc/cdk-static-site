# CDK Static Site


### Getting Started

```
To use this you need domain with ssl certificates configured in 
AWS Route53
```

 1. Create stacks config file, called `cdk.stacks.json` in the root of the project, with content like the following:
```json
[
  {
    "label": "static-site-beta",
    "stage": "beta",
    "domain": "beta.enpython.com",
    "cert_key": "<aws certificate identifier>"
  },
  {
    "label": "static-site-prod",
    "stage": "prod",
    "domain": "enpython.com",
    "cert_key": "<aws certificate identifier>"
  }
]
```
 2. Create environment vars file, called `.env` with the following content:
Replace the values with yours
```
AWS_DEFAULT_REGION=us-east-1
AWS_ACCOUNT_ID=XXXXXX
AWS_ACCESS_KEY_ID=XXXXXXX
AWS_SECRET_ACCESS_KEY=XXXXXXXXX
```
3. Install python virtual environment and cdk
```
$ pipenv --three
$ pipenv install -d
$ pipenv shell

$ npm install -g aws-cdk
```

## Commands

```bash
$ make destroy STACK=static-site-beta
$ make synth STACK=static-site-beta
$ make diff STACK=static-site-beta
$ make deploy STACK=static-site-beta
```

### TODO
 - [ ] Test Deployment for SSR React Sites
 - [ ] Automate Route53 registration of CNAME records