# src/apps/bot/services/bot_service.py

import asyncio
import os

from apps.bot.services.openai_services.assistants_service import (
    AssistantService,
)
from apps.bot.services.openai_services.message_service import MessageService
from apps.bot.services.openai_services.run_service import RunService
from apps.bot.services.openai_services.thread_service import ThreadService


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
            if run.status in ["completed", "failed", "required_action"]:
                break
            await asyncio.sleep(1)

        if run.status == "completed":
            messages = self.message_service.list_messages(thread_id=thread.id)
            return messages.data[0].content[0].text.value
        elif run.status == "required_action":
            tool_outputs = await self.handle_required_action(run)
            if tool_outputs:
                run = self.run_service.submit_tool_outputs_to_run(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=tool_outputs,
                )
                if run.status == "completed":
                    messages = self.message_service.list_messages(
                        thread_id=thread.id
                    )
                    return messages.data[0].content[0].text.value
        return "El proceso está en un estado inesperado."

    async def handle_required_action(self, run):
        tool_outputs = []
        for tool in run.required_action.submit_tool_outputs.tool_calls:
            # Aquí puedes agregar la lógica para manejar las acciones requeridas
            pass
        return tool_outputs
