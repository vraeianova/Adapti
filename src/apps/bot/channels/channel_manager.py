from .whatsapp_channel import WhatsAppChannel


NotImplemented


class ChannelManager:
    def __init__(self):
        self.channels = {
            "whatsapp": WhatsAppChannel(),
            # Can add more channels in the future
            # 'facebook': FacebookChannel(),
            # 'discord': DiscordChannel(),
        }

    def get_channel(self, channel_name):
        return self.channels.get(channel_name)
