import requests
from credentials_img_posting import insta_access_token, insta_user_id
import os
import sqlite3
import logging
import ast
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from urllib.parse import urlparse
import instaloader
# https://developers.facebook.com/docs/instagram-api/guides/content-publishing # insta docs


class PostImg:

    @staticmethod
    def setup_logging():
        """Set up logging"""
        logging.basicConfig(filename='post_operations.log', level=logging.INFO)

    def __init__(self, config):
        for key, value in config.items():
            setattr(self, key, value)
        self.ids = []
        self.post_details = None
        self.ids = []
        self.owner_id = None
        self.hashtags = None
        self.post_id = None  # Initialize post_id to None
        self.public_url = ()
        self.owner_username = ()
        self.top_post = None
        self.db_path=None


    def connect_db(self,):
        if self.db_path is None:
            raise ValueError("Database path is not set.")
            
        try:
            conn = sqlite3.connect(self.db_path)
            print('db connected')
            return conn
        except sqlite3.Error as e:
            logging.error(f"db error: {e}")
            return None  
        
    def get_posted_posts(self):
        """fetch IDs of posts that have been already posted"""
        conn = self.connect_db(self.id_db_path)
        if conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM posted_ids")
            rows = cur.fetchall()
            self.ids = [str(row[0]) for row in rows]
            logging.info(f"IDs fetched: {self.ids}")


    def get_top_post(self):
        """fetch the top post details if it has img and is not already in posted id db"""
        conn = self.connect_db(self.db_path)
        if conn:
            cur = conn.cursor()
            cur.execute("SELECT likesCount, id, hashtags, url FROM insta_hashtag ORDER BY likesCount DESC")
            while True:
                row = cur.fetchone()
                if row is None:
                    logging.info("No more rows to fetch.")
                    break

                self.post_details = {'likes': row[0], 'id': row[1], 'hashtags': row[2], 'url': row[3]}
                img_path = os.path.join('downloaded_images', f'image_{self.post_details["id"]}.jpg')

                if self.post_details['id'] not in self.ids and os.path.exists(img_path):
                    logging.info(f"Suitable post found with ID: {self.post_details['id']}")
                    break


    def google_drive(self):
        """upload image to google drive"""
        try:
            credentials = Credentials.from_service_account_file(self.google_json, scopes=['https://www.googleapis.com/auth/drive'])
            drive_service = build('drive', 'v3', credentials=credentials)
            img_path = os.path.join('downloaded_images', f'image_{self.post_details["id"]}.jpg')

            file_metadata = {'name': os.path.basename(img_path)}
            media = MediaFileUpload(img_path, mimetype='image/jpeg')
            file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            file_id = file.get('id')

            drive_service.permissions().create(fileId=file_id, body={'type': 'anyone', 'role': 'reader'}, fields='id').execute()
            self.post_details['public_url'] = f"https://drive.google.com/uc?export=view&id={file_id}"
            logging.info(f"Public URL created: {self.post_details['public_url']}")

        except Exception as e:
            logging.error(f"Google Drive error: {e}")


    def get_owner_username(self):
        """Fetch the username of the owner of the top post."""
        parsed_url = urlparse(self.post_details['url'])
        path_parts = parsed_url.path.split('/')
        if len(path_parts) >= 2:
            owner_short_code = self.post_details['url'].split('/')[-2]
            L = instaloader.Instaloader()
            post = instaloader.Post.from_shortcode(L.context, owner_short_code)
            self.post_details['owner_username'] = post.owner_username
            logging.info(f"Owner username found: {self.post_details['owner_username']}")

        
    def generate_caption(self):
        """generate caption for the insta post"""
        hashtags = ast.literal_eval(self.post_details.get('hashtags', self.default_hashtags))
        hashtags = ["#" + tag.strip().replace('\"', '') for tag in hashtags]
        self.caption = f'''⅋ 🪡

                        Via. @{self.post_details["owner_username"]}

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
                        {hashtags}'''
        

    def insta_api_post(self):
        """Post the image to Instagram."""
        try:
            url = f"https://graph.facebook.com/v18.0/{self.insta_user_id}/media"
            params = {'image_url': self.post_details['public_url'], 'caption': self.caption, 'access_token': self.insta_access_token}
            response = requests.post(url, params=params)
            container_id = response.json().get('id', 'ID not found')
            publish_url = f"https://graph.facebook.com/v18.0/{self.insta_user_id}/media_publish?creation_id={container_id}&access_token={self.insta_access_token}"
            requests.post(publish_url)
            logging.info(f"Post created: {publish_url}")

        except requests.RequestException as e:
            logging.error(f"Request error: {e}")

    def insert_id(self):
        try:
            conn = sqlite3.connect(self.id_db_path)  
            cursor = conn.cursor()
            if self.post_id is not None:
                cursor.execute("INSERT INTO posted_ids (id) VALUES (?);", (str(self.post_id),))
                conn.commit()
                print(f"Image ID {self.post_id} has been written to posted_ids db.")
                self.ids.append(self.post_id)
            else:
                print("Error: self.post_id is None. Image ID not written to posted_ids db.")

            conn.close()
        except sqlite3.Error as e:
            print(f"db error: {e}")
            logging.error(f"db error: {e}")


 
if __name__ == "__main__":
    PostImg.setup_logging()
    config = {
        "google_json": "D:/coding/instagram/scripts/private/insta-401020-8a55316147d7.json",
        "insta_access_token": insta_access_token,
        "insta_user_id": insta_user_id,
        "default_hashtags": ["gorpcore", "outerwear", "gorp", "gorpcorefashion", "outdoors", "arcteryx", "salomon", "gorpcorestyle", "functionalarchive", "ootd", "explore", "getoutside"],
        "db_path": "D:/coding/instagram/scripts/insta_hashtag.db",
        "id_db_path": "D:/coding/instagram/scripts/posted_ids.db"
    }

    post_img = PostImg(config)
    post_img.get_posted_posts()
    post_img.get_top_post()
    post_img.google_drive()
    post_img.get_owner_username()
    post_img.generate_caption()
    post_img.insta_api_post()
    post_img.insert_id()
    