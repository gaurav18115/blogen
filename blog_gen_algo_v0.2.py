import sys
from urllib.parse import urlparse

import streamlit as st
import xml.etree.ElementTree as ET

from tools.chatgpt import chat_with_open_ai
from tools.file import create_file_with_keyword, append_content_to_file
from tools.logger import log_info, setup_logger
from tools.scraper import fetch_and_parse
from tools.serpapi import get_related_queries, get_image_with_commercial_usage, get_search_urls
from tools.storyblok import post_article_to_storyblok
from tools.subprocess import open_file_with_md_app
from tools.const import OPENAI_TEMPERATURE, SERVICE_NAME, SERVICE_DESCRIPTION, SERVICE_URL
from tokencost import calculate_prompt_cost, calculate_completion_cost

# Step-to-Model Mapping: Define your model preferences here
step_to_model = {
    1: 'gpt-4-turbo-preview', # Outline
    2: 'gpt-3.5-turbo', # Introduction
    3: 'gpt-4-turbo-preview', # Body (...)
    4: 'gpt-4-turbo-preview',
    5: 'gpt-4-turbo-preview',
    6: 'gpt-4-turbo-preview',
    7: 'gpt-4-turbo-preview',
    8: 'gpt-4-turbo-preview',
    9: 'gpt-4-turbo-preview',
    10: 'gpt-4-turbo-preview', # Conclusion
    11: 'gpt-3.5-turbo', # Related Posts
    12: 'gpt-3.5-turbo', # Meta Description
    13: 'gpt-3.5-turbo', # Title
    14: 'gpt-3.5-turbo', # Key Takeaways
    15: 'gpt-3.5-turbo', # ToC
}


steps_prompts = [
    # Step 1
    "Given the primary keywords - {primary_keywords}, the first step will be an outline of the article with 5-6 headings and respective subheadings. "
    "Take into consideration the summary of the first 10 search results for the keyword: {summary_of_search_results}"
    ,
     # Step 2
    "The second step is to write the introduction of the article, without any H2 title. Aim at 50-60 words, be concise yet impactful. "
    ,
    # Step 3
    "You will proceed to write the first point of the outline (if this point doesn't exist, simply don't respond). "
    "If applicable, explain step by step how to do the required actions for the user intent in the keyword provided. "
    "Make sure to follow Google's helpful content guidelines and EEAT (Experience, Expertise, Authoritativeness, and Trustworthiness) into the section creation process. "
    "Whenever relevant include YouTube videos that explain the process, "
    "highlight tools that can help the user, "
    "cover templates that allow the user to simply copy-paste " 
    "and include references to other websites if helpful for the user. "
    ,
    # Step 4
    "You will proceed to write the second point of the outline (if this point doesn't exist, simply don't respond). "
    "If applicable, explain step by step how to do the required actions for the user intent in the keyword provided. "
    "Make sure to follow Google's helpful content guidelines and EEAT (Experience, Expertise, Authoritativeness, and Trustworthiness) into the section creation process. "
    "Whenever relevant include YouTube videos that explain the process, "
    "highlight tools that can help the user, "
    "cover templates that allow the user to simply copy-paste " 
    "and include references to other websites if helpful for the user. "
    ,
    # Step 5
    "You will proceed to write the third point of the outline (if this point doesn't exist, simply don't respond). "
    "If applicable, explain step by step how to do the required actions for the user intent in the keyword provided. "
    "Make sure to follow Google's helpful content guidelines and EEAT (Experience, Expertise, Authoritativeness, and Trustworthiness) into the section creation process. "
    "Whenever relevant include YouTube videos that explain the process, "
    "highlight tools that can help the user, "
    "cover templates that allow the user to simply copy-paste " 
    "and include references to other websites if helpful for the user. "
    ,
    # Step 6
    "You will proceed to write the fourth point of the outline (if this point doesn't exist, simply don't respond). "
    "If applicable, explain step by step how to do the required actions for the user intent in the keyword provided. "
    "Make sure to follow Google's helpful content guidelines and EEAT (Experience, Expertise, Authoritativeness, and Trustworthiness) into the section creation process. "
    "Whenever relevant include YouTube videos that explain the process, "
    "highlight tools that can help the user, "
    "cover templates that allow the user to simply copy-paste " 
    "and include references to other websites if helpful for the user. "
    ,
    # Step 7
    "You will proceed to write the fifth point of the outline (if this point doesn't exist, simply don't respond). "
    "If applicable, explain step by step how to do the required actions for the user intent in the keyword provided. "
    "Make sure to follow Google's helpful content guidelines and EEAT (Experience, Expertise, Authoritativeness, and Trustworthiness) into the section creation process. "
    "Whenever relevant include YouTube videos that explain the process, "
    "highlight tools that can help the user, "
    "cover templates that allow the user to simply copy-paste " 
    "and include references to other websites if helpful for the user. "
    ,
    # Step 8
    "You will proceed to write the sixth point of the outline (if this point doesn't exist, simply don't respond). "
    "If applicable, explain step by step how to do the required actions for the user intent in the keyword provided. "
    "Make sure to follow Google's helpful content guidelines and EEAT (Experience, Expertise, Authoritativeness, and Trustworthiness) into the section creation process. "
    "Whenever relevant include YouTube videos that explain the process, "
    "highlight tools that can help the user, "
    "cover templates that allow the user to simply copy-paste " 
    "and include references to other websites if helpful for the user. "
    ,
    # Step 9
    "You will create a concisive conclusion paragraph, with H2 heading 'Conclusion'. "
    "Define the anchor link with the following format: ## <a name='h2-title'></a>H2 Title "
    ,
    # Step 10
    "You will create five unique Frequently Asked Questions (FAQs) after the conclusion. "
    "The FAQs need to take the keyword into account at all times. "
    "Make sure to add an anchor link to the H2 heading 'Frequently Asked Questions (FAQs)', with two new lines after the heading. "
    "Define the anchor link with the following format: ## <a name='h2-title'></a>H2 Title "
    "The FAQs should have the questions in H3 heading and the answers below (separated by a new line), "
    "with the format: "
    "### Question? "
    "Answer"
    ,
    # Step 11
    "Please create a related posts section (with H2 heading 'Related Posts'), with two new lines after the heading. "
    "Include 3-4 articles that are relevant to this topic out of the existing blog posts described in the sitemap below: {sitemap_urls}. "
    "The bullets should have the title of the article directly with the link to the article - e.g., in markdown [title](link)."
    ,
    # Step 12
    "Please create a meta description (120-140 characters) for the article you just generated."
    ,
    # Step 13
    "Please create 5 variations of a slightly click-baity (to invite the reader to click the link), SEO-optimized title (50-60 characters) for the article below. "
    "Make sure to include the problem it is solving. Avoid futuristic and corporate type of words, phrase it as an How-To or even a Question. "
    "The title should be in the format: 'Keyword: Subtitle', but only if the keyword fits well in the title. Don't use quotes or special characters in the title. "
    "Present the titles in a single line (no bullets or numbers), each separated by a semicolon."
    ,
    # Step 14
    "Create a Key Takeaways section summarising crucial points. "
    "Make sure to use the H2 heading 'Key Takeaways' with two new lines after the heading. "
    "The Key Takeaways should be in bullet format, with the format: "
    "- Takeaway 1"
    "\n- Takeaway 2"
    ,
    # Step 15
    "Create a table of contents (ToC) for the article, only keeping H2 headings and excluding Key Takaways and Introduction. "
    "Do not create a 'Table of Contents' H2 heading. "
    "Make sure to include links to each section in the ToC, with the format: "
    "[H2 Title](#h2-title)"
    ,
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
    payload = {"title": "", "metadescription": "", "intro": "", "body": "", "conclusion": "", "related_posts": "", "faqs": "", "keyword": primary_keywords, "key_takeaways": "", "toc": ""}

    filepath = create_file_with_keyword(primary_keywords)
    log_info(f'🗂️  File Created {filepath}')
    open_file_with_md_app(filepath)

    log_info(f'🎬 Primary Keywords: {primary_keywords}')
    
    summarized_contents = []
    total_cost = 0
    urls = get_search_urls(primary_keywords, number_of_results=10)
    for url in urls:
        content = fetch_and_parse(url)
        if content:
            # Summarize the content using OpenAI
            summarisation_model = "gpt-3.5-turbo"
            summary_prompt = f"Create a knowledge base of the maximum number of tools, templates and references, in 300 words or less: {content[:3000]}"
            summary = chat_with_open_ai([{"role": "user", "content": summary_prompt}], model=summarisation_model) 
            summarized_contents.append(summary)
            prompt_cost = calculate_prompt_cost(summary_prompt, model=summarisation_model)
            completion_cost = calculate_completion_cost(summary, model=summarisation_model)
            total_cost += prompt_cost + completion_cost
            
    if summarized_contents:
        concatenated_summaries = " ".join(summarized_contents)  # Combine all summaries into one large text
        summary_of_search_results_prompt = f"Summarize the following content in 300 words or less, focusing on covering as many tools, templates and references as possible: {concatenated_summaries}"
        summary_of_search_results = chat_with_open_ai([{"role": "user", "content": summary_of_search_results_prompt}], model=summarisation_model) 
        log_info(f"Summary of search results: {summary_of_search_results}\nCost: {total_cost}")
                    
    # Create the system message with primary and secondary keywords
    system_message_1 = f"You are an AI coding writing expert with vast experience in writing techniques and frameworks. "\
                        f"As a skilled content creator, you will craft a 100% unique, human-written, and SEO-optimized article in fluent English that is informative. You will focus exclusively on the keyword provided by the user. "\
                        f"You will write a long-form article that is well-structured and easy to read, with introduction, a body, a conclusion and five unique FAQs. "\
                        f"Use John Gruber's Markdown to format your responses, with appropriate H2 to H4 tags. Use original content, avoid plagiarism, and increase readability. "\
                        f"Avoid bullshitter talk, focus on being helpful, reliable and create people-first content to the reader, as per Google's guidelines: https://developers.google.com/search/docs/fundamentals/creating-helpful-content "\
                        f"Make sure to follow Google's helpful content guidelines and EEAT (Experience, Expertise, Authoritativeness, and Trustworthiness) into the section creation process. "\
                        f"You explain step by step how to do the required actions for the user intent in the keyword provided. Give examples of tools and explain how to use them. Always link to their websites to ensure the credit is given to them (include the links as anchors in the most relevant words). Try to find videos on YouTube that go well with the topic. "\
                        f"Use an informational tone and always reference the sources you use with the website links, including if you are referring to competitors of Emilio as we need to maximize collaboration in the network. "\
                        f"Whenever relevant, introduce Emilio (with website https//getemil.io/)and explain to the user how Emilio can help them with their problem. "\
                        f"Emilio’s is an AI-powered email client designed to save users time. Key functionalities include sorting prioritized emails, summarizing messages and digesting the inbox, drafting emails with the user's tone, and requiring no installation as it operates in the background. The service integrates with the user's existing Gmail account. "\
                        f"The interaction with the user will take several steps below. You will take the necessary time in every step, and do one at a time to ensure the maximum quality possible."

    messages.append({"role": "system", "content": system_message_1})

    sitemap_path = 'sitemap.xml'
    sitemap_urls = load_sitemap_and_extract_urls(sitemap_path)

    i = 1
    total_words = 0
    total_cost = 0
    for step_prompt in steps_prompts:
        # Pre-defined prompt
        prompt = step_prompt.format(primary_keywords=primary_keywords, 
                                    #tone_of_writing=tone_of_writing, 
                                    service_name=service_name, 
                                    service_description=service_description, 
                                    service_url=service_url, 
                                    sitemap_urls=sitemap_urls,
                                    summary_of_search_results=summary_of_search_results
                                    )
        messages.append({"role": "user", "content": prompt})

        model = step_to_model.get(i, 'gpt-4-turbo-preview')  # Fallback to a default model if not specified
        prompt_cost = calculate_prompt_cost(messages, model)
        
        response = chat_with_open_ai(messages, model=model, temperature=OPENAI_TEMPERATURE)
        completion_cost = calculate_completion_cost(response, model)
        total_cost += prompt_cost + completion_cost
        
        messages.append({"role": "assistant", "content": response})

        # Don't append the response of the first step
        if i > 1:
            append_content_to_file(filepath, response, st if CLI else None)
        log_info(f'🔺 ️Completed Step {i}. Words: {len(response.split(" "))}, Cost: {prompt_cost + completion_cost}')
        
        # Capture the response for each section
        if i == 2:  # Assuming intro is captured here
            payload['intro'] += response
        elif 3 <= i <= 8:  # Assuming body is constructed here
            payload['body'] += response + "\n"
        elif i == 9:  # Conclusion
            payload['conclusion'] += response
        elif i == 10:  # FAQs
            payload['faqs'] += response
        elif i == 11:  # Related posts
            payload['related_posts'] += response
        elif i == 12:  # Meta description
            payload['metadescription'] += response
        elif i == 13:  # Title
            payload['title'] += response
        elif i == 14:  # Key Takeaway
            payload['key_takeaways'] += response
        elif i == 15:  # ToC
            payload['toc'] += response

        i += 1
        total_words += len(response.split(" "))
    
    # At the end of the loop, send the payload to Storyblok
    post_article_to_storyblok(payload)
    
    # Read the generated content
    with open(filepath, 'r') as file:
        content = file.read()
    
    log_info(f'Total cost of operation: {total_cost}')

    # Rewrite the file with ToC
    with open(filepath, 'w') as file:
        #file.write(content_with_toc)
        file.write(content)

def run_streamlit_app():
    st.title("📝BLOGEN v0.2 (Blog Generation Algorithm)")

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
            print("Error: keywords not specified.\nUSAGE: python blog_gen_algo_v0.2.py <keywords>")
        while True:
            if _keywords.strip() == "":
                _keywords = input("\nEnter the primary keywords:")
            else:
                break

        log_info('Starting BLOGEN...')
        run_terminal_app(_keywords)

    else:
        run_streamlit_app()
