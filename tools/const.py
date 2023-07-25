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

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'empty-string')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
OPENAI_MAX_TOKENS = int(os.getenv('OPENAI_MAX_TOKENS', 4000))
OPENAI_TEMPERATURE = float(os.getenv('OPENAI_TEMPERATURE', 0.9))
OPENAI_STOP_SEQ = os.getenv('OPENAI_STOP_SEQ', '\n')

SERP_API_KEY = os.getenv('SERP_API_KEY', 'empty-string')

