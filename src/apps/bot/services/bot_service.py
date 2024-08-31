import asyncio
import json
import os

from apps.bot.channels.channel_manager import ChannelManager
from apps.openai.config import OpenAIConfig
from apps.zoho.config import ZohoConfig


class BotService:
    def __init__(self, openai_config=None, zoho_config=None):
        self.channel_manager = ChannelManager()

        if openai_config is None:
            openai_config = OpenAIConfig()
        if zoho_config is None:
            zoho_config = ZohoConfig()

        self.assistant_service = openai_config.get_assistant_service()
        self.thread_service = openai_config.get_thread_service()
        self.run_service = openai_config.get_run_service()
        self.message_service = openai_config.get_message_service()
        self.zoho_booking_service = zoho_config.get_zoho_bookings_service()

    async def handle_message(
        self, message_content, channel_name, recipient_info
    ):
        channel = self.channel_manager.get_channel(channel_name)
        if not channel:
            raise ValueError(
                f"Unsupported communication channel: {channel_name}"
            )

        thread = self.thread_service.create_thread()
        self.message_service.create_message(
            thread_id=thread.id, role="user", content=message_content
        )
        run = self.run_service.create_run(
            thread_id=thread.id, assistant_id=os.getenv("OPENAI_ASSISTANT_ID")
        )

        while True:
            run = await self.run_service.retrieve_run(
                thread_id=thread.id, run_id=run.id
            )
            if run.status in ["completed", "failed", "requires_action"]:
                break
            await asyncio.sleep(1)

        if run.status == "completed":
            messages = await self.message_service.list_messages(
                thread_id=thread.id
            )
            response = messages.data[0].content[0].text.value
        elif run.status == "requires_action":
            response = await self.handle_required_action(run)
        else:
            response = "The process is unexpected."

        await channel.send_message(recipient_info["to_number"], response)
        return response

    async def handle_required_action(self, run):
        tool_outputs = []
        for tool in run.required_action.submit_tool_outputs.tool_calls:
            if tool.function.name == "get_workspaces":
                print("tool used:", tool.function.name)
                arguments = json.loads(tool.function.arguments)
                workspace_id = arguments.get("workspace_id")
                workspace_info = self.zoho_booking_service.get_workspaces(
                    workspace_id
                )
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
