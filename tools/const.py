import os
from dotenv import load_dotenv

load_dotenv()

BLOG_WRITING_TONES = [
    "Informative",
    "Conversational",
    "Inspirational/Motivational",
    "Educational",
    "Humorous",
    "Thought-Provoking",
    "Authoritative",
    "Empathetic",
    "Personal",
    "Argumentative/Persuasive",
    "Storytelling",
    "Expository"
]

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
OPENAI_MAX_TOKENS = int(os.getenv('OPENAI_MAX_TOKENS', 4000))
OPENAI_TEMPERATURE = float(os.getenv('OPENAI_TEMPERATURE', 0.9))
OPENAI_STOP_SEQ = os.getenv('OPENAI_STOP_SEQ', '\n')

STORYBLOK_MANAGEMENTAPI_TOKEN = os.getenv('STORYBLOK_MANAGEMENTAPI_TOKEN', '')
STORYBLOK_CONTENTAPI_TOKEN = os.getenv('STORYBLOK_CONTENTAPI_TOKEN', '')
STORYBLOK_SPACE_ID = os.getenv('STORYBLOK_SPACE_ID', '')

SERP_API_KEY = os.getenv('SERP_API_KEY', '')

SERVICE_NAME = os.getenv('SERVICE_NAME', '')
SERVICE_DESCRIPTION = os.getenv('SERVICE_DESCRIPTION','')
SERVICE_URL = os.getenv('SERVICE_URL', '')

