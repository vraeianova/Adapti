from django.db import models


class Assistant(models.Model):
    assistant_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    instructions = models.TextField()
    model = models.CharField(max_length=100)
    temperature = models.FloatField(default=1.0)
    top_p = models.FloatField(default=1.0)
    response_format = models.CharField(max_length=50, default="auto")
    tools = models.JSONField(default=dict)
    tool_resources = models.JSONField(default=dict)

    def __str__(self):
        return self.name
