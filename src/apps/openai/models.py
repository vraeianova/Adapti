from django.db import models

from apps.customers.models import Customer


class Assistant(models.Model):
    assistant_id = models.CharField(
        max_length=100, unique=True, null=True, blank=True
    )
    customer = models.ForeignKey(
        Customer,
        related_name="customer_assistants",
        on_delete=models.SET_NULL,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    instructions = models.TextField()
    model = models.CharField(max_length=100)
    temperature = models.FloatField(default=1.0)
    top_p = models.FloatField(default=1.0)
    response_format = models.CharField(max_length=50, default="auto")
    tools = models.JSONField(default=dict, null=True, blank=True)
    tool_resources = models.JSONField(default=dict, null=True, blank=True)

    def __str__(self):
        return self.name
