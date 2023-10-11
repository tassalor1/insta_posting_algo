import requests
from credentials import insta_api, insta_user_id
# https://developers.facebook.com/docs/instagram-api/guides/content-publishing

access_token = insta_api
insta_id = insta_user_id
image_url = "https://drive.google.com/uc?export=view&id=1lpEOrNszW_wK3Hxtb0Q3CvJ0nGRkyVIq"
caption = "#"

url = f"https://graph.facebook.com/v18.0/{insta_user_id}/media"
# create container
params = {
    'image_url': image_url,
    'caption': caption,
    'access_token': access_token
}

response = requests.post(url, params=params)

# grabs media object id
container_id = response.json()['id']
#publish pic
publish_url = f"https://graph.facebook.com/v18.0/{insta_user_id}/media_publish?creation_id={container_id}&access_token={access_token}"

response = requests.post(publish_url)
print(response.json())


