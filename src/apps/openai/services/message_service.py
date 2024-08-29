from openai import OpenAI


class MessageService:
    def __init__(self, api_key=None):
        self.client = OpenAI(api_key=api_key)

    def create_message(self, thread_id, role, content):
        return self.client.beta.threads.messages.create(
            thread_id=thread_id, role=role, content=content
        )

    def list_messages(self, thread_id):
        return self.client.beta.threads.messages.list(thread_id=thread_id)
