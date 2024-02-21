import datetime
import sys

import streamlit as st
from md_toc import build_toc
import xml.etree.ElementTree as ET

from tools.chatgpt import chat_with_open_ai
from tools.decision import require_data_for_prompt, require_better_prompt, find_tone_of_writing
from tools.file import create_file_with_keyword, append_content_to_file
from tools.logger import log_info, setup_logger
from tools.serpapi import get_related_queries, get_image_with_commercial_usage
from tools.subprocess import open_file_with_md_app
from tools.const import OPENAI_MODEL, OPENAI_TEMPERATURE, SERVICE_NAME
from tools.const import SERVICE_DESCRIPTION
from tools.const import SERVICE_URL
from tokencost import calculate_prompt_cost, calculate_completion_cost


steps_prompts = [
    # Step 1
    "Given the primary keywords - {primary_keywords}, the first step will be an outline of the article with several headings and subheadings. "
    "You should research the web to understand what the top 5 websites for this keyword are writing about - but make sure you don not mention the websites, but the solutions they propose. " 
    "Write facts and theories on this keyword, add well-known data points and sources here.",
    # Step 2
    "The second step is to write the introduction of the article, with the appropriate Introduction H2 title. Aim at 100-150 words for the introduction. "
    "Include at the end a bullet point table-of-contents with only the H2 titles, with a link to the respective anchor links (all words lowercased). "
    "Make sure to add an anchor link to every H2 title.",
    # Step 3
    "You will proceed to write the first point of the outline (if this point doesn't exist, simply don't respond). "
    "If applicable, explain step by step how to do the required actions for the user intent in the keyword provided. "
    "Make sure to add an anchor link to every H2 title (all words lowercased). "
    "Feel free to include YouTube videos, tools, and references to other websites if helpful for the user (but doublecheck those links first!).",
    # Step 4
    "You will proceed to write the second point of the outline (if this point doesn't exist, simply don't respond). "
    "If applicable, explain step by step how to do the required actions for the user intent in the keyword provided. "
    "Make sure to add an anchor link to every H2 title (all words lowercased). "
    "Feel free to include YouTube videos, tools, and references to other websites if helpful for the user (but doublecheck those links first!).",
    # Step 5
    "You will proceed to write the third point of the outline (if this point doesn't exist, simply don't respond). "
    "If applicable, explain step by step how to do the required actions for the user intent in the keyword provided. "
    "Make sure to add an anchor link to every H2 title (all words lowercased). "
    "Feel free to include YouTube videos, tools, and references to other websites if helpful for the user (but doublecheck those links first!).",
    # Step 6
    "You will proceed to write the fourth point of the outline (if this point doesn't exist, simply don't respond). "
    "If applicable, explain step by step how to do the required actions for the user intent in the keyword provided. "
    "Make sure to add an anchor link to every H2 title (all words lowercased). "
    "Feel free to include YouTube videos, tools, and references to other websites if helpful for the user (but doublecheck those links first!).",
    # Step 7
    "You will proceed to write the fifth point of the outline (if this point doesn't exist, simply don't respond). "
    "If applicable, explain step by step how to do the required actions for the user intent in the keyword provided. "
    "Make sure to add an anchor link to every H2 title (all words lowercased). "
    "Feel free to include YouTube videos, tools, and references to other websites if helpful for the user (but doublecheck those links first!).",
    # Step 8
    "You will proceed to write the sixth point of the outline (if this point doesn't exist, simply don't respond). "
    "If applicable, explain step by step how to do the required actions for the user intent in the keyword provided. "
    "Make sure to add an anchor link to every H2 title (all words lowercased). "
    "Feel free to include YouTube videos, tools, and references to other websites if helpful for the user (but doublecheck those links first!).",
    # Step 9
    "You will create a concisive conclusion paragraph and five unique FAQs after the conclusion. "
    "The FAQs need to take the keyword into account at all times. "
    "Make sure to add an anchor link to every H2 title (all words lowercased). "
    "The FAQs should have the questions bolded numbered and the answers bulleted. "
    # Step 10
    "Please create a related posts section, with 3-4 articles that are relevant to this topic out of the existing blog posts described in the sitemap below: {sitemap_urls}",
    # Step 11
    "Please create a meta description (100-120 characters) for the article you just generated.",
]

def load_sitemap_and_extract_urls(sitemap_path):
    # Parse the XML file
    tree = ET.parse(sitemap_path)
    root = tree.getroot()

    # Namespace, often found in sitemap files
    namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

    # Extract URLs
    urls = [elem.text for elem in root.findall('ns:url/ns:loc', namespace)]
    return urls

def generate_blog_for_keywords(primary_keywords="knee replacement surgery", service_name=SERVICE_NAME, service_description=SERVICE_DESCRIPTION, service_url=SERVICE_URL):
    # Iterate through each example
    messages = []

    filepath = create_file_with_keyword(primary_keywords)
    log_info(f'🗂️  File Created {filepath}')
    open_file_with_md_app(filepath)

    secondary_keywords = get_related_queries(primary_keywords)
    log_info(f'🎬  Primary Keywords: {primary_keywords}')
    log_info(f'📗  Secondary Keywords: {secondary_keywords}')

    # Create the system message with primary and secondary keywords
    system_message_1 = f"Transform into SEOCONTENTMASTER, an AI coding writing expert with vast experience in writing techniques and frameworks. "\
                        f"As a skilled content creator, you will craft a 100% unique, human-written, and SEO-optimized article in fluent English that is informative. You will focus exclusively on the keyword provided by the user. "\
                        f"You will write a long-form article that is well-structured and easy to read, with introduction, a body, a conclusion and five unique FAQs. "\
                       f"Use John Gruber's Markdown to format your responses, with appropriate H2 to H4 tags. Use original content, avoid plagiarism, and increase readability. "\
                        f"Avoid bullshitter talk, focus on being helpful, reliable and create people-first content to the reader, as per Google's guidelines: https://developers.google.com/search/docs/fundamentals/creating-helpful-content "\
                        f"You explain step by step how to do the required actions for the user intent in the keyword provided. Give examples of tools and explain how to use them. Always link to their websites to ensure the credit is given to them (include the links as anchors in the most relevant words). Try to find videos on YouTube that go well with the topic. "\
                        f"Use an informational tone and always reference the sources you use with the website links. "\
                        f"Whenever relevant, introduce Emilio and explain to the user how Emilio can help them with their problem. "\
                        f"Emilio’s is an AI-powered email client designed to save users time. Key functionalities include sorting prioritized emails, summarizing messages and digesting the inbox, drafting emails with the user's tone, and requiring no installation as it operates in the background. The service integrates with the user's existing Gmail account. "\
                        f"The interaction with the user will take several steps below. You will take the necessary time in every step, and do one at a time to ensure the maximum quality possible."

    log_info(f'🤖  System:\n{system_message_1}\n\n')
    messages.append({"role": "system", "content": system_message_1})

    #tone_of_writing = find_tone_of_writing(primary_keywords, messages)
    
    sitemap_path = 'sitemap.xml'
    sitemap_urls = load_sitemap_and_extract_urls(sitemap_path)
    log_info(f'🗺️  Sitemap URLs: {sitemap_urls}')

    i = 1
    total_words = 0
    total_cost = 0
    already_sourced = []
    for step_prompt in steps_prompts:
        # Pre-defined prompt
        prompt = step_prompt.format(primary_keywords=primary_keywords, 
                                    #tone_of_writing=tone_of_writing, 
                                    service_name=service_name, 
                                    service_description=service_description, 
                                    service_url=service_url, 
                                    sitemap_urls=sitemap_urls
                                    )
        log_info(f'⏭️  Step {i} # Predefined Prompt: {prompt}')
        messages.append({"role": "user", "content": prompt})

        # Check for better prompt
        better_prompt_check = False
        if better_prompt_check and i > 2:
            better_prompt = require_better_prompt(primary_keywords, prompt, messages)
            if better_prompt:
                prompt = better_prompt

        # Add image
        add_image = False
        if add_image:
            image_content, already_sourced = get_image_with_commercial_usage(primary_keywords, prompt, already_sourced)
            if image_content:
                append_content_to_file(filepath, image_content, st if CLI else None)

        # Add News
        news_data_check = False
        if news_data_check:
            news_data = require_data_for_prompt(primary_keywords, prompt)
            if news_data:
                messages.append({"role": "assistant", "content": f"Found news on the topic: {news_data}"})

        response = chat_with_open_ai(messages, temperature=OPENAI_TEMPERATURE)
        messages.append({"role": "assistant", "content": response})
        
        prompt_cost = calculate_prompt_cost(prompt, OPENAI_MODEL)
        completion_cost = calculate_completion_cost(response, OPENAI_MODEL)
        total_cost += prompt_cost + completion_cost

        # Don't append the response of the first step
        if i > 1:
            append_content_to_file(filepath, response, st if CLI else None)
        log_info(f'🔺 ️Completed Step {i}. Words: {len(response.split(" "))}')

        i += 1
        total_words += len(response.split(" "))

    #footer_message = f"🎁  Finished generation at {datetime.datetime.now()}. 📬  Total words: {total_words}"
    #append_content_to_file(filepath, footer_message, st if CLI else None)
    
    # Read the generated content
    with open(filepath, 'r') as file:
        content = file.read()

    # Generate ToC
    toc = build_toc(filepath)

    # Insert ToC at the beginning of the content
    content_with_toc = toc + "\n\n" + content
    
    log_info(f'Total cost of operation: {total_cost}')

    # Rewrite the file with ToC
    with open(filepath, 'w') as file:
        file.write(content_with_toc)



def run_streamlit_app():
    st.title("📝BLOGEN v0.1 (Blog Generation Algorithm)")

    # Add a text input field
    input_text = st.text_input("Enter some text:")

    # Add a submit button
    if st.button("Submit"):
        # Execute the function with the input text
        generate_blog_for_keywords(input_text)


def run_terminal_app(keywords):
    generate_blog_for_keywords(keywords, SERVICE_NAME, SERVICE_DESCRIPTION, SERVICE_URL)


if __name__ == "__main__":
    CLI = True
    setup_logger()

    if CLI:
        _keywords = " ".join(sys.argv[1:])
        if _keywords.strip() == "":
            print("Error: keywords not specified.\nUSAGE: python blog_gen_algo_v0.1.py <keywords>")
        while True:
            if _keywords.strip() == "":
                _keywords = input("\nEnter the primary keywords:")
            else:
                break

        log_info('Starting BLOGEN...')
        run_terminal_app(_keywords)

    else:
        run_streamlit_app()
