import json
from typing import Any, Dict

from apps.bot.channels.channel_manager import ChannelManager
from apps.customers.models import Customer
from apps.openai.config import OpenAIConfig
from apps.openai.models import Assistant
from apps.zoho.config import ZohoConfig


class BotService:
    def __init__(
        self,
        openai_config: OpenAIConfig = None,
        zoho_config: ZohoConfig = None,
    ) -> None:
        """
        Initializes the BotService with OpenAI and Zoho configuration services.

        Args:
            openai_config (OpenAIConfig, optional): Configuration for OpenAI services. Defaults to None.
            zoho_config (ZohoConfig, optional): Configuration for Zoho services. Defaults to None.
        """
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

    def handle_message(
        self,
        message_content: str,
        channel_name: str,
        recipient_info: Dict[str, Any],
    ) -> None:
        """
        Handles an incoming message by determining the appropriate assistant and sending a response.

        Args:
            message_content (str): The content of the message received.
            channel_name (str): The communication channel (e.g., 'whatsapp').
            recipient_info (dict): Information about the recipient, including the 'from_number' and 'to_number'.

        Raises:
            ValueError: If the communication channel, customer, or assistant is not found.
        """
        # Get the communication channel
        channel = self.channel_manager.get_channel(channel_name)
        if not channel:
            raise ValueError(
                f"Unsupported communication channel: {channel_name}"
            )

        # Get numbers involved in the communication
        external_customer_number = recipient_info["from_number"]
        clinic_whatsapp_number = recipient_info["to_number"]

        # Look up the customer based on the clinic's WhatsApp number
        try:
            customer = Customer.objects.get(phone=clinic_whatsapp_number)
        except Customer.DoesNotExist:
            raise ValueError(
                f"No customer found for the clinic's WhatsApp number: {clinic_whatsapp_number}"
            )

        # Retrieve the assistant associated with the customer
        try:
            assistant_id = Assistant.objects.get(
                customer=customer
            ).assistant_id
        except Assistant.DoesNotExist:
            raise ValueError(
                f"No assistant found for customer: {customer.name}"
            )

        # Create a new thread and handle the message
        thread = self.thread_service.create_thread()
        self.message_service.create_message(
            thread_id=thread.id, role="user", content=message_content
        )

        # Create a run for the assistant
        run = self.run_service.create_run(
            thread_id=thread.id, assistant_id=assistant_id
        )

        # Handle the run status and respond accordingly
        if run.status == "completed":
            messages = self.message_service.list_messages(thread_id=thread.id)
            response = messages.data[0].content[0].text.value
        elif run.status == "requires_action":
            response = self.handle_required_action(run)
        else:
            response = "The process is unexpected."

        # Send the response back to the external customer
        channel.send_message(
            external_customer_number, response, clinic_whatsapp_number
        )

    def handle_required_action(self, run: Any) -> str:
        """
        Handles any required actions from the assistant's run, such as interacting with tools like Zoho Booking.

        Args:
            run (Any): The run object returned by the assistant, indicating required actions.

        Returns:
            str: The final response after required actions have been handled.
        """
        tool_outputs = []

        # Handle specific tool actions required by the assistant
        for tool in run.required_action.submit_tool_outputs.tool_calls:
            if tool.function.name == "get_workspaces":
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

        # Submit the tool outputs and process the response
        if tool_outputs:
            try:
                run = self.run_service.submit_tool_outputs_to_run(
                    thread_id=run.thread_id,
                    run_id=run.id,
                    tool_outputs=tool_outputs,
                )
                if run.status == "completed":
                    messages = self.message_service.list_messages(
                        thread_id=run.thread_id
                    )
                    response = messages.data[0].content[0].text.value
                else:
                    response = "The process is unexpected."
            except Exception as e:
                print(f"Failed to submit tool outputs: {str(e)}")
                response = (
                    "An error occurred while handling the required action."
                )

        return response
