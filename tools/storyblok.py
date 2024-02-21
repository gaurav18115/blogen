import requests
import json
from tools.const import STORYBLOK_TOKEN, STORYBLOK_SPACE_ID
from tools.logger import log_info

# Variables
oauth_token = STORYBLOK_TOKEN
space_id = STORYBLOK_SPACE_ID


def post_article_to_storyblok(article_data):
    url = f"https://mapi.storyblok.com/v1/spaces/{space_id}/stories/"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"{oauth_token}",
    }
    
    # Structure the payload according to Storyblok's requirements
    payload = {
        "story": {
            "name": article_data["title"],
            "slug": article_data["keyword"].lower().replace(" ", "-"),
            "content": {
                "component": "article",
                "title": article_data["title"],
                "metadescription": article_data["metadescription"],
                "intro": article_data["intro"],
                "body": article_data["body"],
                "conclusion": article_data["conclusion"],
                "related_posts": article_data["related_posts"],
                "faqs": article_data["faqs"]
            }
        },
    }
    
    # For creating a new story
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    print(response)

    # For updating an existing story, use PUT request instead
    # response = requests.put(f"https://mapi.storyblok.com/v1/spaces/{space_id}/stories/{story_id}", json=data, headers=headers)
    
    if response.status_code == 200:
        log_info("Article posted successfully!")
        return response.json()
    else:
        log_info(f"Failed to post article. Status code: {response.status_code}, Message: {response.text}")
        return None