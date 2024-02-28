import requests
import json
from tools.const import STORYBLOK_TOKEN, STORYBLOK_SPACE_ID
from tools.logger import log_info
import markdown

# Variables
oauth_token = STORYBLOK_TOKEN
space_id = STORYBLOK_SPACE_ID


def post_article_to_storyblok(article_data):
    url = f"https://mapi.storyblok.com/v1/spaces/{space_id}/stories/"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"{oauth_token}",
    }
    
    # Convert Markdown fields to HTML
    intro_html = markdown.markdown(article_data["intro"])
    body_html = markdown.markdown(article_data["body"])
    conclusion_html = markdown.markdown(article_data["conclusion"])
    related_posts_html = markdown.markdown(article_data["related_posts"])
    faqs_html = markdown.markdown(article_data["faqs"])
    key_takeaways_html = markdown.markdown(article_data["key_takeaways"])
    toc_html = markdown.markdown(article_data["toc"])
    
    # Structure the payload according to Storyblok's requirements
    payload = {
        "story": {
            "name": article_data["title"],
            "slug": article_data["keyword"].lower().replace(" ", "-").replace("_", "-"),
            "content": {
                "component": "article",
                "title": article_data["title"],
                "metadescription": article_data["metadescription"],
                "intro": intro_html,
                "body": body_html,
                "conclusion": conclusion_html,
                "related_posts": related_posts_html,
                "faqs": faqs_html,
                "key_takeaways": key_takeaways_html,
                "toc": toc_html,
            }
        },
    }
    
    # For creating a new story
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    print(response)

    # For updating an existing story, use PUT request instead
    # response = requests.put(f"https://mapi.storyblok.com/v1/spaces/{space_id}/stories/{story_id}", json=data, headers=headers)
    
    if response.status_code == 200 or response.status_code == 201:
        log_info("Article posted successfully!")
        return response.json()
    else:
        log_info(f"Failed to post article. Status code: {response.status_code}, Message: {response.text}")
        return None
    
def fetch_article_titles():
    url = f"https://api.storyblok.com/v1/cdn/stories?version=published&token={oauth_token}&space_id={space_id}"
    response = requests.get(url)
    if response.status_code == 200:
        articles = response.json().get('stories', [])
        titles = [article['name'] for article in articles]
        return titles
    else:
        log_info(f"Failed to fetch articles. Status code: {response.status_code}, Message: {response.text}")
        return []
