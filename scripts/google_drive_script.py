'''
to upload imgs through the graph api the img file is required to be publicy available through a url. 
this script uploads it to a google drive
'''
import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


# load the service account credentials from json file
credentials = Credentials.from_service_account_file(
    "D:/coding/instagram/scripts/insta-401020-d2b56e3d4162.json",
    scopes=['https://www.googleapis.com/auth/drive']
)

# Build the service object
drive_service = build('drive', 'v3', credentials=credentials)

def upload_to_drive(filename):
    file_metadata = {'name': os.path.basename(filename)}
    media = MediaFileUpload(filename, mimetype='image/jpeg')
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    # make the file publicly accessible and retrieve sharing link
    file_id = file.get('id')
    drive_service.permissions().create(
        fileId=file_id,
        body={'type': 'anyone', 'role': 'reader'},
        fields='id'
    ).execute()

    return f"https://drive.google.com/uc?export=view&id={file_id}"

image_path = "D:/coding/instagram/scripts/downloaded_images/3198999631903343625.jpg"
public_url = upload_to_drive(image_path)
print(f"Public URL: {public_url}")
