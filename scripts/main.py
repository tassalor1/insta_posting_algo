from img_posting.post_img_copy import PostImg
from img_posting.credentials_img_posting import insta_access_token, insta_user_id
import time



def main():
    config = {
        "google_json": "D:/coding/instagram/scripts/private/insta-401020-8a55316147d7.json",
        "insta_access_token": insta_access_token,
        "insta_user_id": insta_user_id,
        "default_hashtags": ["gorpcore","outerwear", "gorp", "gorpcorefashion", "outdoors", 
                             "arcteryx", "salomon", "gorpcorefashion", "gorpcorestyle", "functionalarchive", 
                             "ootd", "explore", "getoutside", '#goretexstudio'],
        "db_path": "D:/coding/instagram/scripts/insta_hashtag.db",
        "id_db_path": "D:/coding/instagram/scripts/posted_ids_new.db"
    }
    
    PostImg.setup_logging()
    post = PostImg(**config)
    
    for _ in range(2):  
        post.get_posted_posts()
        post.get_top_post()
        
        # Check if get_top_post() found a post to process
        if post.post_id is not None:  
            post.get_img()
            post.google_drive()
            post.get_owner_username()
            post.generate_caption()
            post.insta_api_post()
            post.insert_id()
        else:
            print("No suitable post found. Skipping iteration.")

        time.sleep(5)

if __name__ == "__main__":
    main()