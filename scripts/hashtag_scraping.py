from apify_client import ApifyClient
import sqlite3
import json
from credentials import APIFY_API_KEY
import logging
import os
import requests


class Bot():

    def __init__(self, APIFY_API_KEY, hashtags, result_limit, apify_actor, min_likes):
        self.APIFY_API_KEY = APIFY_API_KEY
        self.hashtags = hashtags
        self.result_limit = result_limit
        self.apify_actor = apify_actor
        self.min_likes = min_likes

    def fetch_data(self):
        client = ApifyClient(APIFY_API_KEY)


        posts = []
        post_skip_count = 0

        # call db function to check if id in db
        existing_ids = get_existing_ids()

        for hashtag in self.hashtags:
            run_input = {
                "hashtags": [hashtag],
                "resultsLimit": self.result_limit,
            }

            run = client.actor({self.apify_actor}).call(run_input=run_input)

            # create folder for imgs if it doesnt exist
            if not os.path.exists('downloaded_images'):
                os.makedirs('downloaded_images')

            img_urls = []
            for item in client.dataset(run["defaultDatasetId"]).iterate_items():
                try:
                    if item['likesCount'] >= self.min_likes and item['id'] not in existing_ids:
                        # Download and save the image
                        img_url = item.get('displayUrl', None)
                        if img_url:
                            img_urls.append(img_url)
                        posts.append(item)

                        posts.append(item)
                    else:
                        post_skip_count += 1
                except Exception as e:
                    print(f"Error in processing item: {e}")

        print(f"Skipped {post_skip_count} posts")
        print(f'Fetched {len(posts)} items.')
        return posts


    db_path = "D:\coding\instagram\scripts\insta_hashtag.db"


    def get_existing_ids():
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        # Get the list of existing post IDs from the db
        cur.execute("SELECT id FROM insta_hashtag")
        existing_ids = {row[0] for row in cur.fetchall()}

        return existing_ids


    # Set up logging
    logging.basicConfig(filename='db_operations.log', level=logging.INFO)


    def insert_db(data):
        if not data:
            print("No data to insert.")
            logging.info("No data to insert.")
            return

        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        insert_query = """
        INSERT OR IGNORE INTO insta_hashtag (
            id, type, shortCode, caption, hashtags, mentions, url, commentsCount, 
            dimensionsHeight, dimensionsWidth, 
            displayUrl, images, alt, likesCount, timestamp, ownerId
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """

        rows_inserted = 0

        # Insert into db
        for item in data:
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
                    item.get('ownerId', 'default_ownerId'),
                )
                # Execute the SQL query inside the loop
                cur.execute(insert_query, values)
                if cur.rowcount > 0:
                    rows_inserted += 1
            except Exception as e:
                # If an exception occurs print a message and skip this item
                print(f"Error processing item: {e} - {item}")
                continue

        conn.commit()
        conn.close()

        # Log and print the number of rows inserted
        logging.info(f'{rows_inserted} rows inserted.')
        print(f'{rows_inserted} rows inserted.')


    def db_summary():
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        # Get the total number of rows in the table
        cur.execute("SELECT COUNT(*) FROM insta_hashtag;")
        total_rows = cur.fetchone()[0]

        conn.close()

        # Log and print the database summary
        logging.info(f'Database summary: {total_rows} rows in total.')
        print(f'Database summary: {total_rows} rows in total.')


    def download_images(img_urls):
        if not os.path.exists('downloaded_images'):
            os.makedirs('downloaded_images')
        for idx, img_url in enumerate(img_urls):
            img = requests.get(img_url)
            img_path = os.path.join('downloaded_images', f"image_{idx}.jpg")
            with open(img_path, 'wb') as f:
                f.write(img.content)

config = {
    "APIFY_API_KEY": APIFY_API_KEY,
    "hashtags": ['gorpcore', 'goretexstudio', 'outdoorism', 'gorpcorefashion', 'arcteryx', 'gorpcorestyle', 'outdoorism', 'itsbetteroutside'],
    "result_limit": 50,
    "apify_actor": "apify/instagram-hashtag-scraper"
}
