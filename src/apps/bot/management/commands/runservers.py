# bot/management/commands/runservers.py

import os
from threading import Thread

from django.core.management.base import BaseCommand

from apps.bot.services.communication_channels_services.discord_service import (
    DiscordService,
)


class Command(BaseCommand):
    help = "Run Django and Discord servers concurrently"

    def handle(self, *args, **kwargs):
        django_server_thread = Thread(target=self.run_django_server)
        discord_server_thread = Thread(target=self.run_discord_bot)

        django_server_thread.start()
        discord_server_thread.start()

        django_server_thread.join()
        discord_server_thread.join()

    def run_django_server(self):
        os.system("python src/manage.py runserver")

    def run_discord_bot(self):
        platform_service = DiscordService()
        platform_service.run()
