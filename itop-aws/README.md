# itop-nexmo-aws

The code for the lambdas and the step-function are largely based on [this repository](https://github.com/samanaphone/lambda)

Since then, it has been converted to an AWS serverless app. To setup the AWS tools locally, follow these instructions [here](/itop-aws/AWS-SERVERLESS.md).

This code-base does not configure roles or policies for the functions and the step-function. It also does not configure DynamoDB and function timeout values. Make sure to configure those directly in the AWS console if newly deploying on AWS.