import boto3
import json
import base64
import configparser

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def main():
  # Retrieve variables from Secrets Manager
  secrets_manager = boto3.client('secretsmanager')
  secrets = secrets_manager.get_secret_value(SecretId='arn:aws:secretsmanager:us-west-2:304691913875:secret:gmailreader-j9zfa8')
  
  #Parse secerts as INI file:
  variable_dict = json.loads(secrets['SecretString'])

  bucket_name = variable_dict.get('BUCKET_NAME')
  client_secret = variable_dict.get('CLIENT_SECRET_OBJECT')
  token = variable_dict.get('TOKEN_OBJECT')
  target_folder = variable_dict.get('TARGET_FOLDER')
  credentials = None

  s3 = boto3.client('s3')
  credentials_json = read_json_file_from_s3(s3,bucket_name, client_secret)
  
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  try:
    s3.head_object(Bucket=bucket_name, Key=token)
    token_file_data = read_json_file_from_s3(s3, bucket_name, token)
    credentials = Credentials.from_authorized_user_info(token_file_data, SCOPES)               

  except s3.exceptions.ClientError as e:
    print(e)
    
  # If there are no (valid) credentials available, let the user log in.
  if not credentials or not credentials.valid:
    if credentials and credentials.expired and credentials.refresh_token:
      credentials.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_config(credentials_json, SCOPES)
      credentials = flow.run_local_server(port=0)
      credentials_to_json = credentials.to_json()
      s3.put_object (Body = credentials_to_json, Bucket = bucket_name, Key = token)

   

  try:
    # Call the Gmail API
    service = build("gmail", "v1", credentials=credentials)
    
    query = 'is:unread subject:"My first attempt"'
    result = service.users().messages().list(userId='me', q=query).execute()
    messages = result.get('messages', [])

    if not messages:
        print('No unread messages found with the subject "Important Message".')
    else:
        # Connect to AWS S3
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            attachments = [part for part in msg['payload']['parts'] if part['filename']]

            for attachment in attachments:
              # Ensure the attachmentId is properly padded
              attachment_id = attachment['body']['attachmentId']
              if len(attachment_id) % 4:
                attachment_id += '=' * (4 - len(attachment_id) % 4)

              file_data = base64.urlsafe_b64decode(attachment_id)
              file_name = attachment['filename']


              # Upload the file to S3
              s3.put_object(Bucket=bucket_name, Key=target_folder + file_name, Body=file_data)
              print(f'Uploaded {file_name} to S3 bucket {bucket_name}')
    
  except HttpError as error:
    # TODO(developer) - Handle errors from gmail API.
    print(f"An error occurred: {error}")



#Read object from S3 and return the content as json
def read_json_file_from_s3(s3_client_service, bucket_name, object_key):
  """
    Tries to access an object from S3 and return it as json
    If object exists returns the json otherwise returns  nothing

    Arguments:
    s3_client_service - s3 client instance created
    bucket_name - Name of the bucket where the object is stored
    object_key - prefix of object
  """

  #try to read file from s3
  try:
    response = s3_client_service.get_object(Bucket=bucket_name, Key=object_key)
    json_data = json.loads(response['Body'].read().decode('utf-8'))
    
    return json_data
    
  except Exception as e:
    print(f'Error loading JSON file from S3: {e}')
    return 


if __name__ == "__main__":
  main()
