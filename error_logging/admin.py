from django.contrib import admin

from error_logging.models import ErrorLog


# Register your models here.

class ErrorLogAdmin(admin.ModelAdmin):
    search_fields = ['timestamp', 'level', 'query_parameters', 'message', 'user_agent', 'stack_trace', 'request_path',
                     'method', 'status_code', 'request_time', 'request_method', 'error_source', 'query_parameters']
    list_display = ['id', 'timestamp', 'request_path', 'message', 'request_path', 'error_source', 'user_id']
    list_filter = ['timestamp', 'request_path', 'error_type', 'error_source', 'user_id']


admin.site.register(ErrorLog, ErrorLogAdmin)
