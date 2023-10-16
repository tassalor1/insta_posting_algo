import requests
from credentials_img_posting import insta_api, insta_user_id
import os
import sqlite3
import logging
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
# https://developers.facebook.com/docs/instagram-api/guides/content-publishing # insta docs


class PostImg:

    @staticmethod
    def setup_logging():
        logging.basicConfig(filename='post_operations.log', level=logging.INFO)

    def __init__(self, google_json, insta_access_token, insta_user_id, default_hashtags, db_path):
        self.google_json = google_json
        self.insta_access_token = insta_access_token
        self.insta_user_id = insta_user_id
        self.default_hashtags = default_hashtags
        self.db_path = db_path
        self.ids = []
        self.top_post = None
        self.owner_id = None
        self.hashtags = None
        self.public_url = ()
        self.owner_username = ()
    

        

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
        try:
            with open('posted_ids', 'r') as f:
                self.ids = [line.strip() for line in f]
        except FileNotFoundError:
            logging.warning("posted_ids file not found")
        
    def get_top_post(self):
        conn = self.connect_db()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("SELECT MAX(LikeCount), ownerId, hashtags FROM insta_hashtag")
                self.top_post = cur.fetchone()[0]
                self.owner_id = cur.fetchone()[1]
                self.hashtags = cur.fetchone()[2]

                while self.top_post in self.ids:
                    cur.execute("SELECT MAX(LikeCount), ownerId, hashtags FROM insta_hashtag WHERE LikeCount < ?", (self.top_post,))
                    self.top_post = cur.fetchone()[0]
                    self.owner_id = cur.fetchone()[1]
                    self.hashtags = cur.fetchone()[2]

                logging.info('Top post fetched')

            except sqlite3.Error as e:
                logging.error(f"Database error: {e}")
        else:
            logging.warning("Failed to connect to the database")


    def get_img(self):
        # get matching img for id
        self.img_path = os.path.join('downloaded_images', f'image_{self.top_post}.jpg')
        if os.path.exists(self.img_path):
            logging.info('Matching image fetched')
        else:
            logging.warning('Image not found')
            self.img_path = None


    def google_drive(self):
        try:
            credentials = Credentials.from_service_account_file(
                self.google_json,
                scopes=['https://www.googleapis.com/auth/drive']
            )
            drive_service = build('drive', 'v3', credentials=credentials)

            file_metadata = {'name': os.path.basename(self.img_path)}
            media = MediaFileUpload(self.img_path, mimetype='image/jpeg')
            file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()

            file_id = file.get('id')

            # make the file publicly accessible and retrieve sharing link
            file_id = file.get('id')
            drive_service.permissions().create(
                fileId=file_id,
                body={'type': 'anyone', 'role': 'reader'},
                fields='id'
            ).execute()
            self.public_url = f"https://drive.google.com/uc?export=view&id={file_id}"

            logging.info(f"Public URL: {self.public_url} has been created")

        except Exception as e:
            logging.error(f"Google Drive error: {e}")


    def get_owner_username(self):
        #get username of the author
        try:
            owner_url = f"https://graph.instagram.com/{self.owner_id}?fields=username&access_token={self.insta_access_token}"
            owner_response = requests.get(owner_url)
            owner_data = owner_response.json()
            self.owner_username = owner_data.get('username', 'Username not found')
            logging.info(f'Owner username acquired: {self.owner_username}')

        except requests.RequestException as e:
            logging.error(f"Request error: {e}")

    def generate_caption(self):
        #get hashtags from post or if none default
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
        try:
            response = requests.post(url, params=params)
            print(response.json())
            # grabs media object id
            container_id = response.json().get('id', 'ID not found')
            #publish pic
            publish_url = f"https://graph.facebook.com/v18.0/{self.insta_user_id}/media_publish?creation_id={container_id}&access_token={self.insta_access_token}"

            response = requests.post(publish_url)
            logging.info(response.json())
            print(f'post has been created: {publish_url}')
            # create a file that add posted ids into it
            with open('posted_ids', 'a') as f:
                f.write(str(self.top_post) + '\n')

        except requests.RequestException as e:
            logging.error(f"Request error: {e}")

 
config = {
    "google_json": "D:/coding/instagram/scripts/insta-401020-d2b56e3d4162.json",
    "insta_access_token": insta_api,
    "insta_user_id": insta_user_id,
    "default_hashtags": ["gorpcore","outerwear", "gorp", "gorpcorefashion", "outdoors", 
                         "arcteryx", "salomon", "gorpcorefashion", "gorpcorestyle", "functionalarchive", 
                         "ootd", "explore", "getoutside"],
    "db_path": "D:\coding\instagram\scripts\insta_hashtag.db"
}
if __name__ == "__main__":
    PostImg.setup_logging()
    post = PostImg(**config)
    post.get_posted_posts()
    post.get_top_post()
    post.get_img()
    post.google_drive()
    post.get_owner_username()
    post.generate_caption()
    post.insta_api_post()
    