import asyncio
import json
import os

from apps.services.openai_services import (
    AssistantService,
    MessageService,
    RunService,
    ThreadService,
)
from apps.services.zoho_services import ZohoAuth, ZohoBookingsService


class BotService:
    def __init__(self):
        self.assistant_service = AssistantService(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.thread_service = ThreadService(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.run_service = RunService(api_key=os.getenv("OPENAI_API_KEY"))
        self.message_service = MessageService(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.zoho_auth = ZohoAuth()
        self.zoho_service = ZohoBookingsService(self.zoho_auth)

    async def handle_message(self, message_content):
        thread = self.thread_service.create_thread()
        self.message_service.create_message(
            thread_id=thread.id, role="user", content=message_content
        )
        run = self.run_service.create_run(
            thread_id=thread.id, assistant_id=os.getenv("ASSISTANT_ID")
        )

        while True:
            run = self.run_service.retrieve_run(
                thread_id=thread.id, run_id=run.id
            )
            print("status", run.status)
            if run.status in ["completed", "failed", "requires_action"]:
                break
            await asyncio.sleep(1)

        if run.status == "completed":
            messages = self.message_service.list_messages(thread_id=thread.id)
            print(messages)
            return messages.data[0].content[0].text.value
        elif run.status == "requires_action":
            action_status = await self.handle_required_action(run)
            if action_status == "completed":
                messages = self.message_service.list_messages(
                    thread_id=thread.id
                )
                print("action:", action_status)
                print(messages)
                return messages.data[0].content[0].text.value
            elif action_status == "failed":
                return "Failed execution, please, try again."
        return "The process is unexpected."

    async def handle_required_action(self, run):
        tool_outputs = []
        for tool in run.required_action.submit_tool_outputs.tool_calls:
            if tool.function.name == "get_workspaces":
                print("tool used:", tool.function.name)
                arguments = json.loads(tool.function.arguments)
                workspace_id = arguments.get("workspace_id")
                workspace_info = self.zoho_service.get_workspaces(workspace_id)
                tool_outputs.append(
                    {
                        "tool_call_id": tool.id,
                        "output": json.dumps(workspace_info),
                    }
                )

        if tool_outputs:
            try:
                run = self.run_service.submit_tool_outputs_to_run(
                    thread_id=run.thread_id,
                    run_id=run.id,
                    tool_outputs=tool_outputs,
                )
                print("Tool outputs submitted successfully.")
            except Exception as e:
                print("Failed to submit tool outputs:", e)

        while True:
            run = self.run_service.retrieve_run(
                thread_id=run.thread_id, run_id=run.id
            )
            if run.status in ["completed", "failed"]:
                break
            await asyncio.sleep(1)

        return run.status
