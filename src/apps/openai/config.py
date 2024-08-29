import os

from apps.openai.services import (
    AssistantService,
    MessageService,
    RunService,
    ThreadService,
)


class OpenAIConfig:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

    def get_assistant_service(self):
        return AssistantService(api_key=self.api_key)

    def get_thread_service(self):
        return ThreadService(api_key=self.api_key)

    def get_run_service(self):
        return RunService(api_key=self.api_key)

    def get_message_service(self):
        return MessageService(api_key=self.api_key)
