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
from tools.const import SERVICE_NAME
from tools.const import SERVICE_DESCRIPTION
from tools.const import SERVICE_URL


steps_prompts = [
    # Step 1
    "Step 1: Given the primary keywords - {primary_keywords}, generate a captivating 5-8 words blog title. "
    "After that, write a 40-50 words teaser in {tone_of_writing} tone, "
    "something that creates curiosity and willingness to read more in reader's mind. "
    "Make sure to write in pure markdown format, with the blog title in H1 heading, "
    "and teaser in paragraph format.",
    # Step 2
    "Step 2: On the basis of the user intent for asking {primary_keywords}, set up a base ground of knowledge. "
    "Write facts and theories on this topic, add well-known data points and sources here."
    "Use maximum 300 words for the content. Don't reach any conclusion yet. "
    "\nMake sure to write in pure markdown format, with headings and subheadings (H2 to H3), "
    "paragraphs, lists and text formating (such as bold, italic, strikethrough, etc)."
    "\nLink 2-3 other of my blog posts (found in the sitemap posted below) within the content. "
    "Make sure to sound natural when linking to other blog posts, i.e., the text can only be slightly altered to accommodate a better context for the link. "
    "Make sure to use the anchor text should not be the actual title of the other blog post, but rather something in the text that makes sense. "
    "Sitemap: {sitemap_urls}",
    # Step 3
    "Step 3: On the basis of the user intent for asking {primary_keywords}, describe the problem the user is facing "
    "and give several solutions for it. The solutions cam be either be a process or a product or a service."
    "Use maximum 300 words for the content. Don't reach any conclusion yet."
    "Make sure to write in pure markdown format, with headings and subheadings (H2 to H3), "
    "paragraphs, lists and text formating (such as bold, italic, strikethrough, etc).",
    # Step 4
    "Step 4: Introduce {service_name}, {service_description}"
    "Explain to the user how {service_name} can help them with their problem. "
    "Make sure to link {service_url} in the content. "
    "Use maximum 100 words for the content. Don't reach any conclusion yet. "
    "Make sure to write in pure markdown format, with headings and subheadings (H2 to H3), "
    "paragraphs, lists and text formating (such as bold, italic, strikethrough, etc).",
    # Step 5
    "Step 5: If applicable, demonstrate how to use {service_name} in easy steps. Don't go beyond what is mentioned in the service description: {service_description}. "
    "Use maximum 100 words for the content. Don't reach any conclusion yet. "
    "Make sure to write in pure markdown format, with headings and subheadings (H2 to H3), "
    "paragraphs, lists and text formating (such as bold, italic, strikethrough, etc).",
    # Step 6
    "Step 6: Generate a conclusion based on the content of this blog. Use {tone_of_writing} tone to"
    "ease the user intent to take the next step on {primary_keywords}. "
    "Use maximum 150 words for the content."
    "Make sure to write in pure markdown format, with headings and subheadings (H2 to H3), "
    "paragraphs, lists and text formating (such as bold, italic, strikethrough, etc).",
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
    system_message_1 = f"SYSTEM: Act as an experienced SEO specialist and experienced content writer. " \
                       f"Given a blog with topic {primary_keywords}, help in generating rich content " \
                       f"for SEO optimized blog." \
                       f"Write custom heading for this response. " \
                       f"Naturally use primary Keywords: [{primary_keywords}], and " \
                       f"secondary keywords: [{secondary_keywords}] wherever it fits." \
                       f"Use John Gruber’s Markdown to format your responses." \
                       f"Use original content, avoid plagiarism, increase readability."

    log_info(f'🤖  System:\n{system_message_1}\n\n')
    messages.append({"role": "system", "content": system_message_1})

    tone_of_writing = find_tone_of_writing(primary_keywords, messages)
    
    sitemap_path = 'sitemap.xml'
    sitemap_urls = load_sitemap_and_extract_urls(sitemap_path)
    log_info(f'🗺️  Sitemap URLs: {sitemap_urls}')

    i = 1
    total_words = 0
    already_sourced = []
    for step_prompt in steps_prompts:
        # Pre-defined prompt
        prompt = step_prompt.format(primary_keywords=primary_keywords, 
                                    tone_of_writing=tone_of_writing, 
                                    service_name=service_name, 
                                    service_description=service_description, 
                                    service_url=service_url, 
                                    sitemap_urls=sitemap_urls
                                    )
        log_info(f'⏭️  Step {i} # Predefined Prompt: {prompt}')
        messages.append({"role": "user", "content": prompt})

        # Check for better prompt
        if i > 2:
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
        news_data = require_data_for_prompt(primary_keywords, prompt)
        if news_data:
            messages.append({"role": "assistant", "content": f"Found news on the topic: {news_data}"})

        response = chat_with_open_ai(messages, temperature=0.9)
        messages.append({"role": "assistant", "content": response})

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
