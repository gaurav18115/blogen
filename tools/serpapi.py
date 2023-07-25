from serpapi import GoogleSearch

from tools.const import SERP_API_KEY


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


def get_latest_news(keywords):
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
    for news in news_list[:3]:
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
