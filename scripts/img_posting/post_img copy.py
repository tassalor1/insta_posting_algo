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
        logging.basicConfig(filename='post_operations.log', level=logging.INFO)

    def __init__(self, google_json, insta_access_token, insta_user_id, default_hashtags, db_path, id_db_path):
        self.google_json = google_json
        self.insta_access_token = insta_access_token
        self.insta_user_id = insta_user_id
        self.default_hashtags = default_hashtags
        self.db_path = db_path
        self.id_db_path = id_db_path
        self.ids = []
        self.owner_id = None
        self.hashtags = None
        self.post_id = None
        self.public_url = ()
        self.owner_username = ()
        self.top_post = None


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
            conn_id = sqlite3.connect(self.id_db_path)
            print('id db connected')

            cur_id = conn_id.cursor()
            cur_id.execute("SELECT id FROM posted_ids")
            rows = cur_id.fetchall()

            self.all_ids = set()
            self.all_ids = [str(row[0]) for row in rows]
            print(f"IDs fetched from posted_ids: {self.all_ids}")

            conn_id.close()

        except Exception as e:
            print(f'Database not connected{e}')


    def get_top_post(self):
        print('get_top_post function running')
        conn = self.connect_db()
        if conn:
            cur = conn.cursor()
            cur.execute("SELECT likesCount, id, hashtags, url FROM insta_hashtag ORDER BY likesCount DESC")

            row = cur.fetchone()
            while row is not None:
                self.top_post, self.post_id, self.hashtags, self.url = row


                img_path = os.path.join('downloaded_images', f'image_{self.post_id}.jpg')
                if self.post_id not in self.all_ids and os.path.exists(img_path):
                    print(f"Found suitable post with ID: {self.post_id}")
                    break
                else:
                    row = cur.fetchone()  

            if row is None:
                print("No more rows to fetch.")


    def get_img(self):
        self.img_path = os.path.join('downloaded_images', f'image_{self.post_id}.jpg')
        
        if os.path.exists(self.img_path):
            logging.info('Matching image fetched')
            print('Matching image fetched')
        else:
            logging.warning('Image not found')
            print('Image not found')
 


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
            print(f"Public URL: {self.public_url} has been created")

        except Exception as e:
            logging.error(f"Google Drive error: {e}")


    def get_owner_username(self):
        # get short coe from url
        parsed_url = urlparse(self.url)
        print(self.url)
        path_parts = parsed_url.path.split('/')

        if len(path_parts) >= 2:
            owner_short_code = self.url.split('/')[-2]
            #initialise instaloader
            L = instaloader.Instaloader()
            post = instaloader.Post.from_shortcode(L.context, owner_short_code)

            self.owner_username = post.owner_username
            print(f"owner_username {self.owner_username}")
            logging.info(f"owner_username {self.owner_username}")
        else:
            print("owner_username not found")
            logging.error("owner_username not found")
        
    def generate_caption(self):
        #get hashtags from post or if none default
        if not self.hashtags:
            self.hashtags = self.default_hashtags
            self.hashtags = str(self.hashtags )
            print('post has no hastags')
        hashtags = ast.literal_eval(self.hashtags)
        hashtags = [word.strip().replace('"', '') for word in hashtags]
        hashtags_with_hash = ['#' + tag for tag in hashtags]
        hashtag_final = ' '.join(hashtags_with_hash)
        self.caption = f'''👣 🗻





                        Via. @{self.owner_username}

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
                        {hashtag_final}'''
        

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
            print(self.post_id)

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



 
config = {
    "google_json": "D:/coding/instagram/scripts/private/insta-401020-8a55316147d7.json",
    "insta_access_token": insta_access_token,
    "insta_user_id": insta_user_id,
    "default_hashtags": ["gorpcore","outerwear", "gorp", "gorpcorefashion", "outdoors", 
                         "arcteryx", "salomon", "gorpcorefashion", "gorpcorestyle", "functionalarchive", 
                         "ootd", "explore", "getoutside", '#goretexstudio'],
    "db_path": "D:/coding/instagram/scripts/insta_hashtag.db",
    "id_db_path": "D:/coding/instagram/scripts/posted_ids.db"
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
    post.insert_id()