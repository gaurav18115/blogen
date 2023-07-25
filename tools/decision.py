from tools.chatgpt import chat_with_open_ai
from tools.logger import log_info
from tools.serpapi import get_latest_news


def find_tone_of_writing(primary_keywords, messages):
    new_messages = messages
    new_messages.append({"role": "user", "content": f"Which tones suites best in writing blog on {primary_keywords}? "
                                                    f"Give one word answer."})
    tone_of_writing = chat_with_open_ai(new_messages, temperature=1)
    return tone_of_writing


def require_data_for_prompt(primary_keywords, next_prompt):
    new_messages = [
        {"role": "system", "content": "Act as an experienced SEO specialist and experienced content writer."},
        {"role": "user", "content": f"You will be asked to respond to : {next_prompt} \n\n "
                                    f"Would you require latest news on {primary_keywords}. "
                                    f"Respond with either \"yes\" or \"no\"."}]
    require_news = chat_with_open_ai(new_messages, temperature=1)
    if "yes" in require_news.lower():
        news_data = get_latest_news(primary_keywords, next_prompt)
        log_info(f'🚨  Get News: {news_data}')
        return news_data
    else:
        log_info(f'👷‍  No news')
        return None


def require_better_prompt(primary_keywords, next_prompt, messages):
    new_messages = [
        {"role": "system", "content": "Act as an experienced SEO specialist and experienced content writer."}
    ]
    for previous in messages:
        if previous.get('role') == 'assistant':
            new_messages.append(previous)
    new_messages.append({"role": "user", "content": f"You will be asked to respond to : {next_prompt} \n\n "
                                                    f"Can you suggest a better prompt judging the intent of user: {primary_keywords}. "
                                                    f"Respond with only the prompt that you would ask a SEO specialist "
                                                    f"or simply reply \"no\" if the given prompt is fine."})
    better_prompt = chat_with_open_ai(new_messages, temperature=1)
    if "no" in better_prompt.lower():
        log_info(f'✅  Prompt Ok ')
        return None
    else:
        log_info(f'🍀  Better Prompt: {better_prompt}')
        return better_prompt
