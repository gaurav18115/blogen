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

SERVICE_NAME = os.getenv('SERVICE_NAME', 'Emilio')
SERVICE_DESCRIPTION = os.getenv('SERVICE_DESCRIPTION', "an AI-powered email client designed to enhance email management by automating tasks and providing advanced features that save users time."
                                "The key functionalities include sorting prioritized emails, summarizing messages, drafting emails with the user's tone, and requiring no installation as it operates in the background."
                                "The service integrates with the user's existing email account, starting with Google accounts, and focuses on user privacy and support.")
SERVICE_URL = os.getenv('SERVICE_URL', 'https://getemil.io/')

