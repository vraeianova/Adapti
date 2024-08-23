# src/apps/bot/services/openai_service/message_service.py

import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


class MessageService:
    def __init__(self, api_key=None):
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))

    def create_message(self, thread_id, role, content):
        return self.client.beta.threads.messages.create(
            thread_id=thread_id, role=role, content=content
        )

    def list_messages(self, thread_id):
        return self.client.beta.threads.messages.list(thread_id=thread_id)
