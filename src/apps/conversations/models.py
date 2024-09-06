from django.db import models

from apps.customers.models import Customer
from apps.openai.models import Assistant


class Thread(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True)
    assistant = models.ForeignKey(Assistant, on_delete=models.CASCADE)
    thread_id = models.CharField(max_length=255, unique=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_interaction = models.DateTimeField(null=True, blank=True)
    human_intervention_needed = models.BooleanField(default=False)

    def __str__(self):
        return f"Thread {self.thread_id} - {self.customer.name}"
