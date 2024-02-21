import requests
import json
from tools.const import STORYBLOK_TOKEN, STORYBLOK_SPACE_ID

# Variables
oauth_token = STORYBLOK_TOKEN
space_id = STORYBLOK_SPACE_ID


def post_article_to_storyblok(article_data):
    url = "https://api.storyblok.com/v1/spaces/{space_id}/stories"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {oauth_token}",
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

    # For updating an existing story, use PUT request instead
    # response = requests.put(f"https://api.storyblok.com/v1/spaces/{space_id}/stories/{story_id}", json=data, headers=headers)
    
    if response.status_code == 200:
        print("Article posted successfully!")
        return response.json()
    else:
        print(f"Failed to post article. Status code: {response.status_code}, Message: {response.text}")
        return None