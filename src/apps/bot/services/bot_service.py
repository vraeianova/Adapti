import asyncio
import json
import os

from apps.bot.services.openai_services.assistants_service import (
    AssistantService,
)
from apps.bot.services.openai_services.message_service import MessageService
from apps.bot.services.openai_services.run_service import RunService
from apps.bot.services.openai_services.thread_service import ThreadService

from ..utils import fetch_disabled_court_hours, fetch_dollar_price


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
                print(messages)
                return messages.data[0].content[0].text.value
            elif action_status == "failed":
                return "La ejecución ha fallado, por favor intenta de nuevo."
        return "El proceso está en un estado inesperado."

    async def handle_required_action(self, run):
        tool_outputs = []
        for tool in run.required_action.submit_tool_outputs.tool_calls:
            if tool.function.name == "get_dollar_price":
                dollar_price_info = await fetch_dollar_price()
                tool_outputs.append(
                    {
                        "tool_call_id": tool.id,
                        "output": json.dumps(dollar_price_info),
                    }
                )
            elif tool.function.name == "get_disabled_court_hours":
                arguments = json.loads(tool.function.arguments)
                court_id = arguments["court_id"]
                date = arguments["date"]
                court_hours_info = await fetch_disabled_court_hours(
                    court_id, date
                )
                tool_outputs.append(
                    {
                        "tool_call_id": tool.id,
                        "output": json.dumps(court_hours_info),
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
