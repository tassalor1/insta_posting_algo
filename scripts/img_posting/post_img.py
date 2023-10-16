import requests
from credentials_img_posting import insta_api, insta_user_id
import os
import sqlite3
import logging
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
# https://developers.facebook.com/docs/instagram-api/guides/content-publishing # insta docs


class post_img:

    def __init__(self, google_json, insta_access_token, insta_user_id, image_url, caption, default_hashtags):
        self.google_json = google_json
        self.insta_access_token = insta_access_token
        self.insta_user_id = insta_user_id
        self.image_url = image_url
        self.caption = caption
        self.default_hashtags = default_hashtags

        

    def connect_db(self):
        try:
            conn = sqlite3.connect(self.db_path)
            print('db connected')
            return conn
        except sqlite3.Error as e:
            logging.error(f"db error: {e}")
            return None    
        
    def get_posted_posts(self):
        ## get ids that have been posted to cross reference
        with open('posted_ids', 'r') as f:
             self.ids = [line.strip() for line in f]
        
    def get_top_post(self):
        conn = None
        try:
            conn = self.connect_db()
            cur = conn.cursor()
            cur.execute("SELECT MAX(LikeCount) FROM insta_hashtag")
            self.top_post = cur.fetchone()[0]  

            # check if it has been posted before
            if self.top_post not in self.ids:
                print('top post fetched')
            else:
                return None

        except sqlite3.Error as e:
            logging.error(f"db error: {e}")
            return None

    def get_img(self):
        # get matching img for id
        self.img_path = os.path.join('downloaded_images', f'image_{self.top_post}.jpg')
        if os.path.exists(self.img_path):
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
         # get username of the author of the post
         self.owner_id = self.top_post['ownerId']
         owner_url = f"https://graph.instagram.com/{self.owner_id}?fields=username&access_token={self.insta_access_token}"
         owner_response = requests.get(owner_url)
         owner_data = owner_response.json()
         self.owner_username = owner_data.get('username', 'Username not found')
         print(f'owner user name aquired{self.owner_username}')

    def caption(self):
        #get hashtags from post or if none default
        self.hashtags == None
        self.hashtags = self.top_post['hashtags']
        if self.hashtags == None:
            self.hashtags == self.default_hashtags
            print('post has no hastags')
        
        self.caption = f'''⅋ 🪡

                        Via. {self.owner_username}

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
                        {self.hashtags}'''
        

    def insta_api_post(self):

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
        with open('posted_ids', 'a') as f:
             f.write({self.top_post})
            
 


config = {
    "google_json": "D:/coding/instagram/scripts/insta-401020-d2b56e3d4162.json",
    "insta_access_token": insta_api,
    "insta_user_id": insta_user_id,
    "default_hashtags": ["gorpcore","outerwear", "gorp", "gorpcorefashion", "outdoors", 
                         "arcteryx", "salomon", "gorpcorefashion", "gorpcorestyle", "functionalarchive", 
                         "ootd", "explore", "getoutside"]
}
