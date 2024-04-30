# Gmail Attachement to S3 Pipeline
This project builds and app using aws services that is able to connect to a gmail  account, download the attached file and stores it in S3

## Description
The pipeline loads the necessary  variables from AWS Secrets Manager. In order to be able to authenticate via Oauth, Google requires a client_secret_file and token. Both client_secret_file, and token are stored in S3. When the process runs for the first time, it checks if the token file already exist to complete the authentication proccess.

Before initiating the OAuth authentication process, the Lambda function checks if a token file already exists. If a valid token is found, the function can skip the authentication step and proceed directly to accessing the Gmail account.If no valid token is found, the Lambda function initiates the OAuth authentication process. This involves redirecting the user to a separate page where they can grant permission for the Lambda function to access their Gmail account. After granting permission, the user receives a code that needs to be copied and pasted into the AWS Secrets Manager. This code is then used by the Lambda function to complete the OAuth authentication process. Once the code is stored in the Secrets Manager, you can rerun the Lambda function. It will retrieve the new code and successfully complete the OAuth authentication process, establishing a secure connection with your Gmail account.

With the authenticated connection, your Lambda function can now interact with your Gmail account. In the provided example, the function checks for the latest messages and looks for any attachments. If an attachment is detected, the Lambda function will try to fetch the file and upload it into S3

## Architecture

![GMail API Reader drawio](https://github.com/karmariv/GmailAPIReaderApp/assets/19791050/97f65f6a-0179-47a9-ab83-d5a65e32c6f8)

Tech Stack:
- Google
  - Google Oauth
  - Gmail
- AWS
  - Secret Manager
  - Lambda
  - S3

## Pre-requisites
Before start using the lambda function, some configuration must be done on both Gmail and AWS side
  - GMail
    - Enable Gmail API --> https://support.google.com/googleapi/answer/6158841?hl=en
    - Configure Oauth and consent screen --> https://support.google.com/cloud/answer/6158849?hl=en
  - Lambda
    - Follwing libraries are required google-api-python-client, google-auth-httplib2, google-auth-oauthlib. In order to have them available in lambda you can create a layer. --> https://www.linkedin.com/pulse/add-external-python-libraries-aws-lambda-using-layers-gabe-olokun/


## Additional Resources
- Gmail API documentation -> https://developers.google.com/gmail/api/quickstart/python
- Oauth libraries
    * https://google-auth-oauthlib.readthedocs.io/en/latest/reference/google_auth_oauthlib.flow.html#google_auth_oauthlib.flow.InstalledAppFlow
    * https://googleapis.github.io/google-api-python-client/docs/oauth.html
    * https://google-auth.readthedocs.io/en/stable/reference/google.oauth2.credentials.html#google.oauth2.credentials.Credentials
  



