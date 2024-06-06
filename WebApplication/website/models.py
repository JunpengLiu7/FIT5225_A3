from django.db import models
import uuid
# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=50)

    def __str__(self):
        return (f"{self.username}")

class Record(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    contact_id = models.CharField(max_length=100, blank=True, unique=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=50)
    
    def __str__(self):
        return (f"{self.first_name}{self.last_name}")


class Sender(models.Model):
    phone_number_id = models.CharField(max_length=100)
    access_token = models.CharField(max_length=255)
    url =  models.CharField(max_length=255, default='https://graph.facebook.com/', editable=False)
    version = models.CharField(max_length=255, default='v18.0', editable=False)
    time = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return (f"{self.phone_number_id}")   
    

class Communication_Record(models.Model):
    sender = models.ForeignKey(Sender, on_delete=models.CASCADE)
    contact = models.ForeignKey(Record, on_delete=models.CASCADE)
    message_id = models.CharField(max_length=100, blank=True, unique=True, default=uuid.uuid4, editable=False)
    send_method = models.CharField(max_length=40, default='unknown')
    message_text = models.TextField()
    sent_datetime = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='unknown')
    
    def __str__(self):
        return (f"{self.message_text}")
    

class Group_Record(models.Model):
    group_id = models.CharField(max_length=100, blank=True, unique=True, default=uuid.uuid4, editable=False)
    group_name = models.CharField(max_length=90)
    user = models.ManyToManyField(Record)
    
    def __str__(self):
        return (f"{self.group_name}")
    

class Group_Communication_Record(models.Model):
    sender = models.ForeignKey(Sender, on_delete=models.CASCADE)
    group = models.ForeignKey(Group_Record, on_delete=models.CASCADE)
    group_status = models.CharField(max_length=400, default='unknown')
    send_method = models.CharField(max_length=40, default='unknown')
    group_message_text = models.TextField()
    group_sent_datetime = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return (f"{self.group}{self.group_message_text}")


    
    
