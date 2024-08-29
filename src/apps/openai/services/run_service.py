from openai import OpenAI


class RunService:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    def create_run(self, thread_id, assistant_id):
        return self.client.beta.threads.runs.create(
            thread_id=thread_id, assistant_id=assistant_id
        )

    def list_runs(self, thread_id):
        return self.client.beta.threads.runs.list(thread_id=thread_id)

    def retrieve_run(self, thread_id, run_id):
        return self.client.beta.threads.runs.retrieve(
            thread_id=thread_id, run_id=run_id
        )

    def modify_run(self, thread_id, run_id, **kwargs):
        return self.client.beta.threads.runs.modify(
            thread_id=thread_id, run_id=run_id, **kwargs
        )

    def submit_tool_outputs_to_run(self, thread_id, run_id, tool_outputs):
        return self.client.beta.threads.runs.submit_tool_outputs_and_poll(
            thread_id=thread_id, run_id=run_id, tool_outputs=tool_outputs
        )

    def cancel_run(self, thread_id, run_id):
        return self.client.beta.threads.runs.cancel(
            thread_id=thread_id, run_id=run_id
        )
