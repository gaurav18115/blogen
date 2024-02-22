import requests
from bs4 import BeautifulSoup

def fetch_and_parse(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError if the status is 4xx, 5xx
        soup = BeautifulSoup(response.text, 'html.parser')
        # This is a simplification. You may need to adjust the logic to suit the structure of the specific site
        content = soup.find('body').get_text(separator='\n', strip=True)
        return content
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return None