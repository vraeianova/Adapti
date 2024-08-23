# bot/services/openai_service/assistant_service.py

from openai import OpenAI


class AssistantService:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    def create_assistant(self, **kwargs):
        return self.client.beta.assistants.create(**kwargs)

    def list_assistants(self):
        return self.client.beta.assistants.list()

    def retrieve_assistant(self, assistant_id):
        return self.client.beta.assistants.retrieve(id=assistant_id)

    def modify_assistant(self, assistant_id, **kwargs):
        return self.client.beta.assistants.modify(id=assistant_id, **kwargs)

    def delete_assistant(self, assistant_id):
        return self.client.beta.assistants.delete(id=assistant_id)
