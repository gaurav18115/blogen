from tools.chatgpt import chat_with_open_ai
from tools.storyblok import fetch_articles
import csv

def extract_text(content):
    text = ""
    if isinstance(content, dict):
        if 'content' in content:
            for item in content['content']:
                text += extract_text(item)
        if 'text' in content:
            text += content['text']
    elif isinstance(content, list):
        for item in content:
            text += extract_text(item)
    return text

def preprocess_title(title):
    # Replace new lines with spaces or any other suitable character/formatting
    return title.replace("\n", " ").strip()

def improve_articles_names(articles, csv_filename):
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        # Writing the header of the CSV file
        csvwriter.writerow(['Slug', 'Original Title', 'Suggested Title 1', 'Suggested Title 2', 'Suggested Title 3', 'Suggested Title 4', 'Suggested Title 5'])
        
        # Process only the first 3 articles for testing
        for article in articles:
            slug = article['slug'] 
            name = article['name']
            body = extract_text(article['content']['body'])
            
            prompt = f"""
            Please create 5 variations of a slightly click-baity (to invite the reader to click the link), SEO-optimized title (50-60 characters) for the article below. 
            The keyword associated with the article is '{slug}'.
            Make sure to include the problem it is solving. Avoid futuristic and corporate type of words, phrase it as an How-To or even a Question. 
            The title should be in the format: 'Keyword: Subtitle', but only if the keyword fits well in the title. Don't use quotes or special characters in the title. 
            Present the titles in a single line (no bullets or numbers), each separated by a semicolon. Respond only with the titles, no need to include any other information.
            \nArticle: \n{body}
            """
            
            suggested_names_str = chat_with_open_ai([{"role": "user", "content": prompt}], model='gpt-3.5-turbo')
            suggested_names = suggested_names_str.split(';')
            
            # Preprocess each suggested title to handle new lines
            suggested_names = [preprocess_title(title) for title in suggested_names]
            
            # Ensure that there are exactly 5 suggested titles
            suggested_names = suggested_names[:5] + [''] * (5 - len(suggested_names))
            
            csvwriter.writerow([slug, name] + suggested_names)
            
if __name__ == "__main__":
    articles = fetch_articles()
    improve_articles_names(articles, 'suggested_titles.csv')
