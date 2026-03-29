from django.contrib import admin
from .models import Patient, Billing

admin.site.register(Patient)
admin.site.register(Billing)