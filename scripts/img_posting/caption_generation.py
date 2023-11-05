import openai
from credentials_img_posting import openai_key


def generate_caption():
    openai.api_key = openai_key
    background_info = (
        "Craft a slick, nine-word max caption that nods to gorpcore enthusiasts. "
        "Avoid sales tones; speak the insider language of outdoor hipster. Include one fitting emoji. No hashtags"
    )
    # Your image description goes here
    image_description = "A photo of a serene mountain lake at sunrise."

    # Combine the background with the specific image description
    prompt = f"{background_info}"

    response = openai.Completion.create(
      engine="gpt-3.5-turbo-instruct",
      prompt=prompt,
      max_tokens=60
    )

    # Extract the caption
    caption = response.choices[0].text.strip()
    print("Suggested Caption:", caption)
    return caption
