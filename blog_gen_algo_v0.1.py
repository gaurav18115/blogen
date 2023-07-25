import datetime
import sys

import streamlit as st

from tools.chatgpt import chat_with_open_ai
from tools.decision import require_data_for_prompt, require_better_prompt
from tools.file import create_file_with_keyword, append_content_to_file
from tools.logger import log_info, setup_logger
from tools.serpapi import get_latest_news, get_related_queries
from tools.subprocess import open_file_with_default_app

steps_prompts = [
    # Step 1
    "Step 1: INTRODUCTION\nFor the topic - {primary_keywords}, generate a captivating blog title."
    "Followed with an introduction in {tone_of_writing} tone. "
    "Something that creates curiosity and willingness to read more in reader's mind."
    "Use maximum 150 words for the content.",
    # Step 2
    "Step 2: TONE\nFigure out the intent of the {primary_keywords} and generate the outline of this blog. "
    "Use the {tone_of_writing} tone to give contextual awareness to the user."
    "Use maximum 200 words for the content.",
    # Step 3
    "Step 3: ISSUE\nBased on the intent of the {primary_keywords}, set up a base ground of knowledge. "
    "Write facts and theories on this topic, add well-known data points and sources here."
    "Use maximum 250 words for the content.",
    # Step 4
    "Step 4: REMEDY\nBased on {primary_keywords}, describe the problem the user is facing and "
    "give your solution for it. The solution could be either be a process or a product or a service."
    "Use maximum 300 words for the content.",
    # Step 5
    "Step 5: OPTIONS\nWhy the solution we are providing is the best solution. "
    "Estimate the best use case or application where this solution fits well."
    "Provide other substitutes which optimizes money and time. "
    "Use maximum 250 words for the content.",
    # Step 6
    "Step 6: PROS AND CONS\nThis is optional. If there are pros and cons to certain options, "
    "then list those items. Change the heading with positive and negative phrases"
    "Use maximum 250 words for the content.",
    # Step 7
    "Step 7: IMPLEMENTATION\nIf applicable, demonstrate how to use our solution in easy steps."
    "Use maximum 250 words for the content.",
    # Step 8
    "Step 8: CONCLUSION\nGenerate a conclusion based on the content of this blog. Use {tone_of_writing} tone to"
    "ease the user intent to take the next step on {primary_keywords}. Express a quick thanks with a positive footnote."
    "Use maximum 200 words for the content.",
]


def generate_blog_for_keywords(primary_keywords="knee replacement surgery"):
    # Iterate through each example
    messages = []

    filepath = create_file_with_keyword(primary_keywords)
    open_file_with_default_app(filepath)

    secondary_keywords = get_related_queries(primary_keywords)
    log_info(f'🎬 Primary Keywords: {primary_keywords}')
    log_info(f'📗Secondary Keywords: {secondary_keywords}')

    # Create the system message with primary and secondary keywords
    system_message = f"Act as an experienced SEO specialist and experienced content writer. " \
                     f"Given a blog with topic {primary_keywords}, help in generating rich content " \
                     f"for SEO optimized blog. Use John Gruber’s Markdown to format your responses." \
                     f"There are {len(steps_prompts)} steps that constitute the different sections." \
                     f"Write custom heading for Naturally use primary Keywords: [{primary_keywords}], and " \
                     f"secondary keywords: [{secondary_keywords}] wherever it fits."

    log_info(f'🤖System:\n{system_message}\n')

    messages.append({"role": "system", "content": system_message})
    messages.append({"role": "user", "content": f"Which tones suites best in writing blog on {primary_keywords}? "
                                                f"Give one word answer."})
    tone_of_writing = chat_with_open_ai(messages, temperature=1)
    log_info(f'🗂️File Created {filepath}')

    i = 1
    total_words = 0
    for step_prompt in steps_prompts:
        # Pre-defined prompt
        prompt = step_prompt.format(primary_keywords=primary_keywords, tone_of_writing=tone_of_writing)
        log_info(f'🪜Step {i} # Predefined Prompt: {prompt}')
        messages.append({"role": "user", "content": prompt})

        if i > 2:
            better_prompt = require_better_prompt(primary_keywords, prompt)
            if better_prompt:
                prompt = better_prompt

        news_data = require_data_for_prompt(primary_keywords, prompt)
        if news_data:
            messages.append({"role": "assistant", "content": f"Found news on the topic: {news_data}"})

        response = chat_with_open_ai(messages, temperature=0.9)
        messages.append({"role": "assistant", "content": response})

        append_content_to_file(filepath, response, st if CLI else None)
        log_info(f'✔️Completed Step {i}. Words: {len(response.split(" "))}')

        i += 1
        total_words += len(response.split(" "))

    footer_message = f"🏁Finished generation at {datetime.datetime.now()}. Total words: {total_words}"
    append_content_to_file(filepath, footer_message, st if CLI else None)


def run_streamlit_app():
    st.title("📝BLOGEN v0.1 (Blog Generation Algorithm)")

    # Add a text input field
    input_text = st.text_input("Enter some text:")

    # Add a submit button
    if st.button("Submit"):
        # Execute the function with the input text
        generate_blog_for_keywords(input_text)


def run_terminal_app(keywords):
    generate_blog_for_keywords(keywords)


if __name__ == "__main__":
    CLI = True
    setup_logger()

    if CLI:
        keywords = " ".join(sys.argv[1:])
        if keywords.strip() == "":
            print("Error: keywords not specified.\nUSAGE: python blog_gen_algo_v0.1.py <keywords>")
        while True:
            if keywords.strip() == "":
                keywords = input("\nEnter the primary keywords:")
            else:
                break

        log_info('Starting BLOGEN...')
        run_terminal_app(keywords)

    else:
        run_streamlit_app()
