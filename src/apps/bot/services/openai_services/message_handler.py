# src/apps/bot/services/openai_service/message_handler.py

import asyncio
import json
import os

from dotenv import load_dotenv

from apps.bot.services.openai_services.run_service import RunService
from apps.bot.services.openai_services.thread_service import ThreadService
from apps.bot.utils import fetch_disabled_court_hours, fetch_dollar_price


load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")

thread_service = ThreadService(api_key=OPENAI_API_KEY)
run_service = RunService(api_key=OPENAI_API_KEY)


async def handle_message(message_content):
    try:
        thread = thread_service.create_thread()
        thread_service.create_message(
            thread_id=thread.id, role="user", content=message_content
        )

        run = run_service.create_run(
            thread_id=thread.id, assistant_id=ASSISTANT_ID
        )

        while True:
            run = run_service.retrieve_run(thread_id=thread.id, run_id=run.id)
            if run.status in ["completed", "failed", "required_action"]:
                break
            await asyncio.sleep(1)

        if run.status == "completed":
            messages = thread_service.list_messages(thread_id=thread.id)
            assistant_message_content = messages.data[0].content[0].text.value
            return assistant_message_content
        elif run.status == "required_action":
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
                    run = run_service.submit_tool_outputs_to_run(
                        thread_id=thread.id,
                        run_id=run.id,
                        tool_outputs=tool_outputs,
                    )
                except Exception as e:
                    print("Failed to submit tool outputs:", e)

                if run.status == "completed":
                    messages = thread_service.list_messages(
                        thread_id=thread.id
                    )
                    assistant_message_content = (
                        messages.data[0].content[0].text.value
                    )
                    return assistant_message_content
                else:
                    return "El proceso está en un estado inesperado."
        elif run.status == "failed":
            return "La ejecución ha fallado, por favor intenta de nuevo."
        else:
            return "El proceso está en un estado inesperado."
    except Exception as e:
        print(f"Error: {e}")
        return "Ocurrió un error técnico al procesar tu solicitud."
