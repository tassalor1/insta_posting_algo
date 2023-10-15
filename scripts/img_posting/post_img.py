import requests
from scripts.data_pull.credentials import insta_api, insta_user_id
import os
import sqlite3
import logging
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
# https://developers.facebook.com/docs/instagram-api/guides/content-publishing # insta docs


class post_img:

    def __init__(self, google_json, insta_access_token, insta_user_id, image_url, caption):
        self.google_json = google_json
        self.insta_access_token = insta_access_token
        self.insta_user_id = insta_user_id
        self.image_url = image_url
        self.caption = caption

        

    def connect_db(self):
        try:
            conn = sqlite3.connect(self.db_path)
            print('db connected')
            return conn
        except sqlite3.Error as e:
            logging.error(f"db error: {e}")
            return None    
        
    def get_top_post(self):
        conn = None
        try:
            conn = self.connect_db()
            cur = conn.cursor()
            cur.execute("SELECT MAX(LikeCount) FROM insta_hashtag")
            self.top_post = cur.fetchone()[0]  

            # check if it has been posted before
            if self.top_post not in self.get_posted_posts():
                print('top post fetched')
            else:
                return None

        except sqlite3.Error as e:
            logging.error(f"db error: {e}")
            return None

    def get_img(self):

        self.img_path = os.path.join('downloaded_images', f'image_{self.top_post}.jpg')
        if os.path.exists(self.img_path ):
            print('matching img fetched')
        else:
            return None


    def google_drive(self):
        # load the service account credentials from json file
        credentials = Credentials.from_service_account_file(
            self.google_json,
            scopes=['https://www.googleapis.com/auth/drive']
        )
        # Build the service object
        drive_service = build('drive', 'v3', credentials=credentials)

        file_metadata = {'name': os.path.basename(self.img_path)}
        media = MediaFileUpload(self.img_path, mimetype='image/jpeg')
        file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()

        # make the file publicly accessible and retrieve sharing link
        file_id = file.get('id')
        drive_service.permissions().create(
            fileId=file_id,
            body={'type': 'anyone', 'role': 'reader'},
            fields='id'
        ).execute()
        self.public_url = f"https://drive.google.com/uc?export=view&id={file_id}"

        print(f"Public URL: {self.public_url} has been created")


    def get_owner_username(self):
         # call api to get owner username from there id

    def insta_api_post(self):


        self.caption = "⅋ 🪡

                        Via. self.author

                        —————————————————-
                        𝘍𝘰𝘭𝘭𝘰𝘸 @clavext 𝘧𝘰𝘳 𝘮𝘰𝘳𝘦 𝘤𝘰𝘯𝘵𝘦𝘯𝘵
                        .
                        .
                        .
                        .
                        .
                        .
                        .
                        .
                        self.hashtags git "

        url = f"https://graph.facebook.com/v18.0/{self.insta_user_id}/media"
        # create container
        params = {
            'image_url': self.public_url,
            'caption': self.caption,
            'access_token': self.insta_access_token
        }

        response = requests.post(url, params=params)

        # grabs media object id
        container_id = response.json()['id']
        #publish pic
        publish_url = f"https://graph.facebook.com/v18.0/{insta_user_id}/media_publish?creation_id={container_id}&access_token={self.insta_access_token}"

        response = requests.post(publish_url)
        print(response.json())

        # create a file that add posted ids into it
        with open(wb') as f:

    def get_posted_posts(self):
        ## open posted id file
        with open() 'wb') as f:
    pass


config = {
    "google_json": "D:/coding/instagram/scripts/insta-401020-d2b56e3d4162.json",
    "insta_access_token": insta_api,
    "insta_user_id": insta_user_id
}
