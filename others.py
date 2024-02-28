from tools.chatgpt import chat_with_open_ai
from tools.storyblok import fetch_articles

import { renderRichText } from "@storyblok/astro";


def improve_titles_with_gpt(articles):
    # Process only the first 3 articles for testing
    for article in articles[:3]:
        slug = article['slug'] 
        title = article['name']
        body = article['content']['body']
        
        prompt = "Please create 5 variations of a slightly click-baity (to invite the reader to click the link), SEO-optimized title (50-60 characters) for the article below. "
        f"The keyword associated with the article is '{slug}'."
        "Make sure to include the problem it is solving. Avoid futuristic and corporate type of words, phrase it as an How-To or even a Question. "
        "The title should be in the format: 'Keyword: Subtitle', but only if the keyword fits well in the title. Don't use quotes or special characters in the title. "
        "Present the titles in a single line (no bullets or numbers), each separated by a semicolon. Respond only with the titles, no need to include any other information."
        f"\nArticle: \n{body}"
        
        print(f"Original title: '{title}'\n")
        print(f"body: '{body}'\n")
        
        #improved_title = chat_with_open_ai([{"role": "user", "content": prompt}], model='gpt-3.5-turbo')
        
        #print(f"Original title: '{title}'\nImproved titles: '{improved_title}'\n")

if __name__ == "__main__":
    articles=fetch_articles()
    improve_titles_with_gpt(articles)