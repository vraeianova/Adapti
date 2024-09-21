import json
from typing import Any, Dict

from django.utils import timezone

from apps.api.serializers.appointments_serializers import (
    AppointmentCreateSerializer,
    AppointmentSerializer,
)
from apps.bot.channels.channel_manager import ChannelManager
from apps.conversations.models import Thread
from apps.doctors.models import Doctor
from apps.openai.config import OpenAIConfig
from apps.openai.models import Assistant
from apps.patients.models import Patient
from apps.zoho.config import ZohoConfig


class BotService:
    def __init__(
        self,
        channel_name: str,
        openai_config: OpenAIConfig = None,
        zoho_config: ZohoConfig = None,
    ) -> None:
        """
        Initializes the BotService with OpenAI and Zoho configuration services.
        """
        self.channel_manager = ChannelManager()

        if openai_config is None:
            openai_config = OpenAIConfig()
        if zoho_config is None:
            zoho_config = ZohoConfig()
        # zoho_config = None

        self.assistant_service = openai_config.get_assistant_service()
        self.thread_service = openai_config.get_thread_service()
        self.run_service = openai_config.get_run_service()
        self.message_service = openai_config.get_message_service()
        self.zoho_booking_service = zoho_config.get_zoho_bookings_service()

        self.channel = self.channel_manager.get_channel(channel_name)
        if not self.channel:
            raise ValueError(
                f"Unsupported communication channel: {channel_name}"
            )

    def handle_message(
        self,
        message_content: str,
        recipient_info: Dict[str, Any],
    ) -> None:
        """
        Handles an incoming message by determining the appropriate assistant and sending a response.
        """
        external_customer_phone = recipient_info["from_number"]
        company_whatsapp_number = recipient_info["to_number"]
        print("company wha", company_whatsapp_number)
        # Obtener el cliente (empresa) y el asistente
        # company = self._get_customer_by_phone(company_whatsapp_number)
        assistant = Assistant.objects.get(
            company__phone=company_whatsapp_number
        )

        # Intentar obtener un thread existente para este cliente y asistente
        thread, created = Thread.objects.get_or_create(
            external_customer_phone=external_customer_phone,  # El número de teléfono del cliente externo
            assistant=assistant,  # La empresa (representada por Assistant)
            defaults={"thread_id": "openai_thread_id"},
        )

        if created:
            # Si se creó un nuevo thread, se imprime un mensaje
            print(
                f"Created a new thread for {external_customer_phone} with {assistant.company.name}"
            )
        else:
            # Si ya existía, actualizar el campo 'last_interaction'
            thread.last_interaction = timezone.now()
            thread.save(
                update_fields=["last_interaction"]
            )  # Solo actualizar el campo 'last_interaction'
            print(
                f"Updated 'last_interaction' for existing thread {thread.thread_id}"
            )

        # Verificar si es necesaria la intervención humana
        if self.is_human_intervention_required(thread):
            print("Human intervention is required for this thread.", thread)
            return  # Detener si necesita intervención humana

        # If no human intervention is required, continue with processing
        self.process_message(
            message_content,
            thread,
            assistant,
            self.channel,
            external_customer_phone,
            company_whatsapp_number,
        )

    def is_human_intervention_required(self, thread: Thread) -> bool:
        """
        Checks if a thread requires human intervention.

        Args:
            thread (Thread): The conversation thread.

        Returns:
            bool: True if human intervention is required, False otherwise.
        """
        return thread.human_intervention_needed

    def process_message(
        self,
        message_content,
        thread,
        assistant,
        channel,
        external_customer_number,
        company_whatsapp_number,
    ):
        """
        Processes the message normally with OpenAI unless human intervention is required.
        """
        # Create the thread in OpenAI if it's a new one
        if not thread.thread_id or thread.thread_id == "openai_thread_id":
            openai_thread = self.thread_service.create_thread()
            thread.thread_id = openai_thread.id
            thread.save()

        # Add message to the thread
        self.message_service.create_message(
            thread_id=thread.thread_id, role="user", content=message_content
        )

        # Create a run for the assistant
        run = self.run_service.create_run(
            thread_id=thread.thread_id, assistant_id=assistant.assistant_id
        )
        print("verify run", run)
        print("verify run status", run.status)
        # Handle the run status and respond accordingly
        if run.status == "completed":
            messages = self.message_service.list_messages(
                thread_id=thread.thread_id
            )
            response = messages.data[0].content[0].text.value
        elif run.status == "requires_action":
            print("Requires action")
            response = self.handle_required_action(run, thread)
        else:
            response = "The process is unexpected."

        # Send the response back to the external customer
        channel.send_message(
            external_customer_number, response, company_whatsapp_number
        )

    def create_appointment(
        self, appointment_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Crea una cita llamando directamente al serializador de creación de citas.

        Args:
            appointment_data (Dict[str, Any]): Los datos necesarios para crear una cita.

        Returns:
            Dict[str, Any]: Los datos de la cita creada o un mensaje de error.
        """
        # Usar el serializador para validar y guardar la cita
        serializer = AppointmentCreateSerializer(data=appointment_data)

        if serializer.is_valid():
            # Si los datos son válidos, guarda la cita y retorna los datos
            appointment = serializer.save()
            return AppointmentSerializer(appointment).data
        else:
            # Si los datos no son válidos, devolver los errores
            return {
                "error": "Failed to create appointment",
                "details": serializer.errors,
            }

    def handle_required_action(self, run: Any, thread: Thread) -> str:
        """
        Handles any required actions from the assistant's run, such as interacting with tools like Zoho Booking.

        Args:
            run (Any): The run object returned by the assistant, indicating required actions.
            thread (Thread): The current conversation thread.

        Returns:
            str: The final response after required actions have been handled.
        """
        tool_outputs = []

        # Handle specific tool actions required by the assistant
        for tool in run.required_action.submit_tool_outputs.tool_calls:
            if tool.function.name == "create_appointment":
                try:
                    print("creating appointment...")
                    appointment_data = json.loads(tool.function.arguments)

                    # Llamada directa al serializador de creación de citas
                    appointment_response = self.create_appointment(
                        appointment_data
                    )

                    if "error" not in appointment_response:
                        tool_outputs.append(
                            {
                                "tool_call_id": tool.id,
                                "output": json.dumps(appointment_response),
                            }
                        )
                    else:
                        tool_outputs.append(
                            {
                                "tool_call_id": tool.id,
                                "output": "Failed to create appointment.",
                            }
                        )
                except Exception as e:
                    print(f"Error while creating appointment: {str(e)}")
                    tool_outputs.append(
                        {
                            "tool_call_id": tool.id,
                            "output": "Error in processing appointment creation.",
                        }
                    )
            if tool.function.name == "get_doctors":
                print("doctors")
                doctors = list(
                    Doctor.objects.filter().values(
                        "id", "first_name", "last_name", "specialization"
                    )
                )
                tool_outputs.append(
                    {
                        "tool_call_id": tool.id,
                        "output": json.dumps(doctors),
                    }
                )
            if tool.function.name == "create_patient":
                print("creating patient...")
                arguments = json.loads(tool.function.arguments)
                name = arguments.get("name")
                email = arguments.get("email")
                phone_number = arguments.get("phone_number")
                address = arguments.get("address")

                patient = Patient()
                patient.name = name
                patient.email = email
                patient.phone_number = phone_number
                patient.address = address
                patient.save()

                print("patient created", patient)
                tool_outputs.append(
                    {
                        "tool_call_id": tool.id,
                        "output": json.dumps(patient.id),
                    }
                )
            if tool.function.name == "get_workspaces":
                arguments = json.loads(tool.function.arguments)
                workspace_id = arguments.get("workspace_id")
                workspace_info = self.zoho_booking_service.get_workspaces(
                    workspace_id
                )
                print("verificar workspaces info", workspace_id)
                tool_outputs.append(
                    {
                        "tool_call_id": tool.id,
                        "output": json.dumps(workspace_info),
                    }
                )
            if tool.function.name == "detect_human_intervention":
                # Mark the thread as needing human intervention
                thread.human_intervention_needed = True
                thread.save()
                tool_outputs.append(
                    {
                        "tool_call_id": tool.id,
                        "output": "Responde que en breve recibirá asistencia",
                    }
                )

        # Submit the tool outputs and process the response
        if tool_outputs:
            print("submiting tool")
            try:
                run = self.run_service.submit_tool_outputs_to_run(
                    thread_id=run.thread_id,
                    run_id=run.id,
                    tool_outputs=tool_outputs,
                )
                print("process running", run)
                print("process running status", run.status)
                if run.status == "completed":
                    print("process completed")
                    messages = self.message_service.list_messages(
                        thread_id=run.thread_id
                    )
                    response = messages.data[0].content[0].text.value

                elif run.status == "requires_action":
                    print("Requires action again")
                    response = self.handle_required_action(run, thread)

                else:
                    print("probablemente entre aqui")
                    response = "The process is unexpected."
            except Exception as e:
                print(f"Failed to submit tool outputs: {str(e)}")
                response = (
                    "An error occurred while handling the required action."
                )

        return response
