from django.contrib.auth.models import User
from django.db import models


# Create your models here.


class ErrorLog(models.Model):
    """The ErrorLog model is designed to store information related to error handling. All types of error generated in
    Front-End or Back-End. Log error and display them in admin panel."""
    Error_Source = [
        ('Front-End', 'Front-End'),
        ('Back-End', 'Back-End'),
    ]
    Error_Type = [
        ('Error', 'Error'),
        ('Debug', 'Debug'),
    ]
    timestamp = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    level = models.CharField(max_length=1000, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    stack_trace = models.TextField(null=True, blank=True)
    request_path = models.CharField(max_length=1000, null=True, blank=True)
    user_agent = models.CharField(max_length=1000, null=True, blank=True)
    method = models.CharField(max_length=1000, null=True, blank=True)
    status_code = models.IntegerField(null=True, blank=True)
    request_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    request_method = models.CharField(max_length=1000, null=True, blank=True)
    user_id = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='error_logs')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    error_source = models.CharField(max_length=10, choices=Error_Source, null=True, blank=True)
    error_type = models.CharField(max_length=10, choices=Error_Type, null=True, blank=True)
    query_parameters = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.level

    class Meta:
        verbose_name = 'Error Log'
        verbose_name_plural = 'Error Logs'
