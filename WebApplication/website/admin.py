from django.contrib import admin
from .models import Record, Communication_Record, Group_Record, Sender, Group_Communication_Record


# Register your models here.
admin.site.register([Record, Communication_Record, Group_Record, Sender, Group_Communication_Record])
