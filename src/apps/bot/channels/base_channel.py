from abc import ABC, abstractmethod


class BaseCommunicationChannel(ABC):

    @abstractmethod
    def send_message(self, to_number, message_body):
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def receive_message(self, request):
        raise NotImplementedError("Subclasses must implement this method.")
