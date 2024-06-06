from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.forms import ModelForm
from .models import Record, Group_Record, Sender, Communication_Record, Group_Communication_Record

# Add Record Form

class AddRecordForm(forms.ModelForm):
    first_name = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder": "First Name",  "class": "form-control"}), label="")
    last_name = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder": "Last Name",  "class": "form-control"}), label="")
    phone = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder": "Phone Number",  "class": "form-control", "type":"number"}), label="")
    email = forms.CharField(widget=forms.widgets.TextInput(attrs={"placeholder": "Email Address",  "class": "form-control"}), label="")
    
    class Meta:
        model = Record
        exclude = ("User", )

        
class AddGroupForm(forms.ModelForm):
    
    group_name = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder": "Group Name",  "class": "form-control"}), label="")
    user = forms.ModelMultipleChoiceField(required=True, queryset=Record.objects, widget=forms.CheckboxSelectMultiple())
    
    class Meta:
        model = Group_Record
        exclude = ("User", )
        
class AddSenderForm(forms.ModelForm):
    phone_number_id = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder": "Phone_ID",  "class": "form-control", "type":"number"}), label="")
    access_token = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder": "Token",  "class": "form-control"}), label="")
    class Meta:
        model = Sender
        exclude = ("User", )
        
class ChatMessageForm(forms.ModelForm):
    sender = forms.ModelChoiceField(required=True, queryset=Sender.objects)
    contact = forms.ModelChoiceField(required=True, queryset=Record.objects)
    message_text = forms.CharField(widget=forms.Textarea(attrs={"rows":3, "placeholder": "Type Message"}))
    
    
    class Meta:
        model = Communication_Record
        fields = ['sender', 'contact', 'message_text']
        widgets = {
            'sender': forms.Select(attrs={'class':'form-control'}),
            'contact': forms.Select(attrs={'class':'form-control'}),
            'message_text': forms.Textarea(attrs={'class':'form-control'}),
        }

class ChatGroupMessageForm(forms.ModelForm):
    sender = forms.ModelChoiceField(required=True, queryset=Sender.objects)
    group = forms.ModelChoiceField(required=True, queryset=Group_Record.objects)
    group_message_text = forms.CharField(widget=forms.Textarea(attrs={"rows":3, "placeholder": "Type Message"}))
    
    
    class Meta:
        model = Group_Communication_Record
        fields = ['sender', 'group', 'group_message_text']
        widgets = {
            'sender': forms.Select(attrs={'class':'form-control'}),
            'group': forms.Select(attrs={'class':'form-control'}),
            'message_text': forms.Textarea(attrs={'class':'form-control'}),
        }