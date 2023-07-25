from tools.chatgpt import chat_with_open_ai
from tools.logger import log_info
from tools.serpapi import get_latest_news


def require_data_for_prompt(primary_keywords, next_prompt):
    new_messages = [
        {"role": "system", "content": "Act as an experienced SEO specialist and experienced content writer."},
        {"role": "user", "content": f"You will be asked to respond to : {next_prompt} \n\n "
                                    f"Would you require latest news on {primary_keywords}. "
                                    f"Respond with either \"yes\" or \"no\"."}]
    require_news = chat_with_open_ai(new_messages, temperature=1)
    if "yes" in require_news.lower():
        news_data = get_latest_news(next_prompt)
        log_info(f'🚨Get News: {news_data}')
        return news_data
    else:
        log_info(f'👷‍No news')
        return None


def require_better_prompt(primary_keywords, next_prompt):
    new_messages = [
        {"role": "system", "content": "Act as an experienced SEO specialist and experienced content writer."},
        {"role": "user", "content": f"You will be asked to respond to : {next_prompt} \n\n "
                                    f"Would you rather change the prompt judging the intent of user: {primary_keywords}. "
                                    f"Respond with the prompt that you would ask a SEO specialist "
                                    f"or simply reply \"no\" if the given prompt is fine."}]
    required_prompt = chat_with_open_ai(new_messages, temperature=1)
    if "no" in required_prompt.lower():
        log_info(f'✅Prompt Check ')
        return None
    else:
        log_info(f'🍀Better Prompt: {required_prompt}')
        return required_prompt
