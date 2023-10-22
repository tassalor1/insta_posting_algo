import requests
from credentials_img_posting import insta_access_token, insta_user_id
import os
import sqlite3
import logging
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
        print('get_top_post function running')
        conn = self.connect_db()
        if conn:
            cur = conn.cursor()
            cur.execute("SELECT MAX(likesCount), id, hashtags, url FROM insta_hashtag")
            row = cur.fetchone()
            #loop till post has matching downlaoded img
            
            while row:
                self.top_post, self.post_id, self.hashtags, self.url = row
                
                img_path = os.path.join('downloaded_images', f'image_{self.post_id}.jpg')
                
                if os.path.exists(img_path):
                    break  
            
                # If image doesn't exist, fetch next row with smaller likesCount
                cur.execute("SELECT MAX(likesCount), id, hashtags, url FROM insta_hashtag WHERE likesCount < ?", (self.post_id))
                row = cur.fetchone()
               
            if row is None:
                print("No more rows to fetch.")
                logging.info('No more rows to fetch')


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
        path_parts = parsed_url.path.split('/')

        if len(path_parts) >= 2:
            owner_short_code = path_parts[2]
            #initialise instaloader
            L = instaloader.Instaloader()
            post = instaloader.Post.from_shortcode(L.context, owner_short_code)

            self.owner_username = post.owner_username
            print(f"owner_username {self.owner_username}")
            logging.info(f"owner_username {self.owner_username}")
        else:
            print("owner_username not found")
            logging.error("owner_username not found")
        

        
            #get username of the author using api
        # try:
        #     owner_url = f"https://graph.instagram.com/{self.owner_id}?fields=username&access_token={self.insta_access_token}"
        #     owner_response = requests.get(owner_url)
        #     owner_response.raise_for_status()
        #     owner_data = owner_response.json()
        #     self.owner_username = owner_data.get('username', 'Username not found')
        #     logging.info(f'Owner username acquired: {self.owner_username}')
        #     print(f'Owner username acquired: {self.owner_username}')

        # except requests.RequestException as e:
        #     logging.error(f"Request error: {e}")
        #     print(f"Request error: {e}")

    def generate_caption(self):
        import ast
        #get hashtags from post or if none default
        if self.hashtags == None:
            self.hashtags == self.default_hashtags
            print('post has no hastags')
        hashtags = ast.literal_eval(self.hashtags)
        hashtags = [word.strip().replace('"', '') for word in hashtags]
        hashtags_with_hash = ['#' + tag for tag in hashtags]
        hashtag_final = ' '.join(hashtags_with_hash)
        self.caption = f'''⅋ 🪡

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
            # create a file that add posted ids into it
            with open('posted_ids', 'a') as f:
                f.write(str(self.top_post) + '\n')

        except requests.RequestException as e:
            logging.error(f"Request error: {e}")

 
config = {
    "google_json": "D:/coding/instagram/scripts/private/insta-401020-8a55316147d7.json",
    "insta_access_token": insta_access_token,
    "insta_user_id": insta_user_id,
    "default_hashtags": ["gorpcore","outerwear", "gorp", "gorpcorefashion", "outdoors", 
                         "arcteryx", "salomon", "gorpcorefashion", "gorpcorestyle", "functionalarchive", 
                         "ootd", "explore", "getoutside"],
    "db_path": "D:/coding/instagram/scripts/insta_hashtag.db"
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
    