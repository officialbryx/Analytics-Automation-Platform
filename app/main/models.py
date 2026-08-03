from django.db import models

# Create your models here.
class Requests(models.Model):
    STATUS = (
        ("running", "RUNNING"),
        ("retrying", "RETRYING"),
        ("finished", "FINISHED"),
        ("failure", "FAILURE"),
        ("cancelled", "CANCELLED"),
    )

    task_id = models.CharField(unique=True)
    status = models.CharField(max_length=9, choices=STATUS, default="running")
    logs = models.TextField(null=True, blank=True)

    request_name = models.CharField()
    information = models.TextField()
    requester_email = models.EmailField()

    class Meta:
        verbose_name = "Request"
        verbose_name_plural = "Requests"

    def __str__(self):
        return self.request_name
