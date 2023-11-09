from apify_client import ApifyClient
import sqlite3
import json
from credentials_data_pull import APIFY_API_KEY
import logging
import os
import requests
import time
 

class Bot:

    @staticmethod
    def setup_logging():
        logging.basicConfig(filename='db_operations.log', level=logging.INFO)

    def __init__(self, **config):
        for key, value in config.items():
            setattr(self, key, value)
        self.posts = []
        self.img_urls = []

    def connect_db(self):
        try:
            conn = sqlite3.connect(self.db_path)
            return conn
        except sqlite3.Error as e:
            logging.error(f"db error: {e}")
            return None
        

    def get_existing_ids(self):
        conn = self.connect_db()
        if conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM insta_hashtag")
            existing_ids = {row[0] for row in cur.fetchall()}
            conn.close()
            return existing_ids
        return set()


    def fetch_data(self):
        self.client = ApifyClient(self.APIFY_API_KEY)
        self.existing_ids = self.get_existing_ids()
        run_count = 0

        for hashtag in self.hashtags:
            run_input = {
                "hashtags": [hashtag],
                "resultsLimit": self.result_limit,
                "proxyConfiguration": self.proxy_config
            }
            self.run = self.client.actor(self.apify_actor).call(run_input=run_input)
            self.process_items()

            time.sleep(90)
            run_count += 1
            logging.info(f"Skipped {self.post_skip_count} posts")
            logging.info(f"Fetched {len(self.posts)} items")
            print(f"Run count: {run_count} = {hashtag}")
        

    # check post has certain likes and not already in db
    def process_items(self):
        for item in self.client.dataset(self.run["defaultDatasetId"]).iterate_items():
            if item['likesCount'] >= self.min_likes and item['id'] not in self.existing_ids:
                print(item)
                self.posts.append(item)
                img_url = item.get('displayUrl')
                if img_url:
                    self.img_urls.append(img_url)
            else:
                self.post_skip_count += 1
        

    def insert_db(self):
        if not self.posts:
            print(self.posts)
            logging.info("No data to insert")
            return
        
        conn = self.connect_db()
        if conn:
            cur = conn.cursor()
            rows_inserted = 0

            insert_query = """
            INSERT OR IGNORE INTO insta_hashtag (
                id, type, shortCode, caption, hashtags, mentions, url, commentsCount, 
                dimensionsHeight, dimensionsWidth, 
                displayUrl, images, alt, likesCount, timestamp, ownerId
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """

            rows_inserted = 0

            # insert into db
            for item in self.posts:
                print(item)
                try:
                    values = (
                        item['id'],
                        item.get('type', 'default_type'),
                        item.get('shortCode', 'default_shortCode'),
                        item.get('caption', 'default_caption'),
                        json.dumps(item.get('hashtags', [])),
                        json.dumps(item.get('mentions', [])),
                        item.get('url', 'default_url'),
                        item.get('commentsCount', 0),
                        item.get('dimensionsHeight', 0),
                        item.get('dimensionsWidth', 0),
                        item.get('displayUrl', 'default_displayUrl'),
                        json.dumps(item.get('images', [])),
                        item.get('alt', 'default_alt'),
                        item.get('likesCount', 0),
                        item.get('timestamp', 'default_timestamp'),
                        item.get('ownerId', 'default_ownerId') 

                    )

                    cur.execute(insert_query, values)
                    if cur.rowcount > 0:
                        rows_inserted += 1
                except sqlite3.Error as e:
                    logging.error(f"db error: {e}")

            logging.info(f'{rows_inserted} rows inserted')
            print(f'{rows_inserted} rows inserted')
            conn.commit()
            conn.close()
            logging.info(f"{rows_inserted} rows inserted")


    def db_summary(self):
        conn = self.connect_db()
        if conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM insta_hashtag")
            total_rows = cur.fetchone()[0]
            conn.close()
            logging.info(f"DB summary: {total_rows} rows in total")


    def download_images(self):
        os.makedirs('downloaded_images', exist_ok=True)
        img_count = 0
        for idx, img_url in enumerate(self.img_urls):
            try:
                img = requests.get(img_url)
                img.raise_for_status()
                img_path = os.path.join('downloaded_images', f"image_{idx}.jpg")
                with open(img_path, 'wb') as f:
                    f.write(img.content)
                img_count += 1
                logging.info(f"Successfully downloaded image {idx+1} of {len(self.img_urls)}")

            except requests.RequestException as e:
                logging.error(f"Failed to download image {idx+1} due to {e}")
            time.sleep(1) 

        print(f"Successfully downloaded {img_count} out of {len(self.img_urls)} images")
        logging.info(f"Successfully downloaded {img_count} out of {len(self.img_urls)} images")

                 
if __name__ == "__main__":
    Bot.setup_logging()
    config = {
    "APIFY_API_KEY": APIFY_API_KEY,
    "hashtags": ['gorp', 'gorpcore', 'goretexstudio', 'goretexstudio', 'salomon',  'nikeacg',  'patagonia','gorpcorefashion', 'arcteryx', 'gorpcorestyle', 'outdoorism', 'itsbetteroutside'],
    "result_limit": 10,
    "apify_actor": "apify/instagram-hashtag-scraper",
    "min_likes": 1,
    "db_path": "D:\coding\instagram\scripts\insta_hashtag.db",
    "post_skip_count": 0,
    "img_urls": [],
    "proxy_config": {'useApifyProxy': True,'apifyProxyGroups': ['BUYPROXIES94952']}
}

    bot = Bot(**config)
    bot.fetch_data()
    bot.insert_db()
    bot.db_summary()
    bot.download_images()
