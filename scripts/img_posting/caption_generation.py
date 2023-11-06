import openai
from credentials_img_posting import openai_key


def generate_caption():
    openai.api_key = openai_key
    background_info = (
        "Create a caption that adheres to the following rules: "
        "No hashtags. Include one fitting emoji. It should be slick, a maximum of nine words, "
        "nod to gorpcore enthusiasts, avoid sales tones, speak the insider language "
        "of outdoor hipsters."
    )



    # Combine the background with the specific image description
    prompt = f"{background_info}\nRemember, do not use hashtags."

    response = openai.completions.create(
      model="gpt-3.5-turbo-instruct",
      prompt=prompt, 
      max_tokens=60,
      temperature=0.5,
    )

    
    caption = response.choices[0].text.strip() # extract caption
    caption = caption.replace('#', '') # replace hashtag if it doesnt follow rules
    caption = caption.replace('"', '')
    print("Suggested Caption:", caption)
    return caption

generate_caption()