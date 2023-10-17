'''
this script will download files again if main did not
'''

import os
import sqlite3
import requests

def download_missing_images(db_path):
 
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
   
    cur.execute("SELECT id, displayUrl FROM insta_hashtag")
    records = cur.fetchall()
    

    conn.close()
    img_count = 0
    # Iterate over each record and download the image if it doesn't exist
    for record in records:
        post_id, display_url = record
        img_path = os.path.join('downloaded_images', f'image_{post_id}.jpg')
        
        
        if not os.path.exists(img_path):
            try:
                img = requests.get(display_url)
                
               
                with open(img_path, 'wb') as f:
                    f.write(img.content)
                print(f"Downloaded image for post {post_id}")
                img_count += 1

            except Exception as e:
                print(f"Failed to download image for post {post_id}. Error: {e}")
    print(f"Successfully downloaded {img_count}")

    print({img_count})

if __name__ == '__main__':
    db_path = "D:\coding\instagram\scripts\insta_hashtag.db" 
    download_missing_images(db_path)
