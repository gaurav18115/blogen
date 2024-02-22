from serpapi import GoogleSearch

from tools.chatgpt import chat_with_open_ai
from tools.const import SERP_API_KEY
from tools.logger import log_info

def get_search_urls(keyword, number_of_results=5):
    params = {
        "engine": "google",
        "q": keyword,
        "api_key": SERP_API_KEY,
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    search_results = results.get("organic_results", [])
    urls = [result["link"] for result in search_results[:number_of_results]]
    return urls


def get_related_queries(keyword):
    params = {
        "engine": "google_trends",
        "q": keyword,
        "data_type": "RELATED_QUERIES",
        "api_key": SERP_API_KEY
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    related_queries = results.get("related_queries", {})

    # Extract rising and top queries separately and combine them into a single list
    rising_queries = [query["query"] for query in related_queries.get("rising", [])]
    top_queries = [query["query"] for query in related_queries.get("top", [])]
    all_queries = rising_queries[:2] + top_queries[:2]

    return ", ".join(all_queries)


def get_latest_news(keywords, prompt):
    messages = [
        {"role": "user", "content": f"Act as an experienced SEO specialist and experienced content writer. "
                                    f"Given keywords - [{keywords}], and a prompt [{prompt}] "
                                    f"Find the necessary 2-3 keywords related to primary keywords "
                                    f"from the given prompt to search news from Google News. "
                                    f"Respond only with those keywords comma separated"}
    ]
    keywords = chat_with_open_ai(messages, temperature=1)

    log_info(f'🈂️  Keywords for news: {keywords}')
    params = {
        "engine": "google",
        "q": keywords,
        "tbm": "nws",
        "api_key": SERP_API_KEY
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    # Extract news results and format them into a consumable string
    news_list = results.get("news_results", [])
    news_string = ""
    for news in news_list[:5]:
        title = news.get("title", "")
        link = news.get("link", "")
        source = news.get("source", "")
        published_date = news.get("published_date", "")
        summary = news.get("snippet", "")

        news_string += f"Title: {title}\n"
        news_string += f"Link: {link}\n"
        news_string += f"Source: {source}\n"
        news_string += f"Published Date: {published_date}\n"
        news_string += f"Summary: {summary}\n\n"

    return news_string


def get_image_with_commercial_usage(keywords, prompt, already_sourced):
    messages = [
        {"role": "user", "content": f"Act as an experienced SEO specialist and experienced content writer. "
                                    f"Given primary keywords - [{keywords}], and a prompt [{prompt}] "
                                    f"Find the necessary 2-3 keywords related to primary keywords "
                                    f"from the given prompt to search images from Google Images. "
                                    f"Respond only with those keywords comma separated."}
    ]
    keywords = chat_with_open_ai(messages, temperature=1)
    if "no" in keywords.lower():
        return None, already_sourced

    log_info(f'🏞️  Keywords for image: {keywords}')
    params = {
        "engine": "google",
        "q": keywords,
        "tbm": "isch",
        "tbs": "sur:fmc",
        "api_key": SERP_API_KEY
    }
    search = GoogleSearch(params)
    results = search.get_dict()

    image_results = results.get("images_results", [])

    for image in image_results:
        image_source = image.get("source", "")
        image_url = image.get("original", "")
        if image_source in already_sourced or image_url in already_sourced:
            continue
        already_sourced.append(image_source)
        already_sourced.append(image_url)
        image_title = image.get("title", "")
        image_content = f"![{image_title}]({image_url})\n Source: {image_source}\n\n"
        return image_content, already_sourced

    return None, already_sourced
