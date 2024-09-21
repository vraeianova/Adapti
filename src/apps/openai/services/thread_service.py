from openai import OpenAI


class ThreadService:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    def create_thread(self, **kwargs):
        return self.client.beta.threads.create(**kwargs)

    def list_threads(self):
        return NotImplemented

    def retrieve_thread(self, thread_id):
        return self.client.beta.threads.retrieve(thread_id=thread_id)

    def delete_thread(self, thread_id):
        return self.client.beta.threads.delete(thread_id=thread_id)

    def create_thread_and_run(self, **kwargs):
        return self.client.beta.threads.create_and_run(**kwargs)
