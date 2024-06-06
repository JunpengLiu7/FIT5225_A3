from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Record, Communication_Record, Group_Record, Sender, Group_Communication_Record
from .forms import AddRecordForm, AddGroupForm, AddSenderForm, ChatMessageForm, ChatGroupMessageForm
from django import template
import json,random, string, time, requests, re, phonenumbers, copy
from phonenumbers import carrier
from phonenumbers.phonenumberutil import number_type
from website import decode_jwt
from email_validator import validate_email, EmailNotValidError
from django.http import HttpResponse, JsonResponse, HttpResponseNotAllowed, HttpResponseBadRequest
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.safestring import mark_safe
from .pageination import Pagination
from django.http.request import QueryDict
from django.http import HttpResponse
from django.http import JsonResponse
from cognitojwt import jwt_sync
import time


def validate_au_mobile(number):
    try:
        parsed_number = phonenumbers.parse(number, "AU")
        return number_type(parsed_number) == phonenumbers.PhoneNumberType.MOBILE
    except phonenumbers.phonenumberutil.NumberFormatException:
        return False

def validate_phone(number):
    try:
        parsed_number = phonenumbers.parse(number)
        return carrier._is_mobile(number_type(parsed_number))
    except phonenumbers.phonenumberutil.NumberFormatException:
        return False


def is_email_valid(email):
    try:
        emailinfo = validate_email(email, check_deliverability=False)
        email = emailinfo.normalized
        return True
    except EmailNotValidError as e:
        print(str(e))
        return False

# Create your views here.
def sendWAMessage(phoneNumber, message, token):
    string = 'Bearer '
    full_token = string + token
   
  
    headers = {"Authorization": full_token}
    payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phoneNumber,
            "type": "text",
            "text": {"body":message}  
               }
    respone = requests.post(settings.WHATSAPP_URL, headers=headers, json=payload)
    
    # ans = respone.json()
    
    if respone.status_code == 200:
        return True
    else:
        return False
   
@csrf_exempt
def whatsAppWebhook(request):
    if request.method =='GET':
        VERIFY_TOKEN = '4eee0753-2969-4c14-9bc7-387234169bc5'
        mode = request.GET['hub.mode']
        token = request.GET['hub.verify_token']
        challenge = request.GET['hub.challenge']
        
        if mode == 'subscribe' and token ==  VERIFY_TOKEN:
            return HttpResponse(challenge, status=200)
        else:
            return HttpResponse('error', status=403)
    
    if request.method =='POST':
        data = json.loads(request.body)
        print(data)
        if 'object' in data and 'entry' in data:
            if data['object'] == 'whatsapp_business_account':
                try:
                    for entry in data['entry']:
                        phoneNumber = entry['changes'][0]['value']['metadata']['display_phone_number']
                        # print(phoneNumber)
                        phoneID = entry['changes'][0]['value']['metadata']['phone_number_id']
                        # print(phoneID,'look here')
                        profileName = entry['changes'][0]['value']['contacts'][0]['profile']['name']
                        whatsAppID = entry['changes'][0]['value']['contacts'][0]['wa_id']
                        fromID = entry['changes'][0]['value']['messages'][0]['from']
                        # print(fromID)
                        messageID = entry['changes'][0]['value']['messages'][0]['id']
                        timestamp = entry['changes'][0]['value']['messages'][0]['timestamp']
                        text = entry['changes'][0]['value']['messages'][0]['text']['body']
                        # print(text)
                        print(Record.objects.filter(phone=str(fromID)).exists())
                        if Record.objects.filter(phone=str(fromID)).exists()== True:
                            print('yes')
                            message_sender = Record.objects.get(phone=str(fromID))
                            message_receiver = Sender.objects.get(phone_number_id=str(phoneNumber))
                            print('look here')
                            print(message_sender,message_receiver)
                            received_message = Communication_Record.objects.create(sender=message_receiver,contact=message_sender,message_text=text,send_method='Individual Response',status='received')
                            print('received_message')
                            received_message.save()
                            print('yes')
                            
                        
                        
                        # message = 'RE: {} was received'.format(text)
                        # message = '2'
                        # token = 'EAAO1oqsZAGHUBO6UOy4vzHncBwb8YWliGSZBl7cmAmlbsluBKiAUbTZCx7y1aOom2tib3zvrXUeZB5dOjbKB3x9dHqq1CVNQsM4wgWwZAqQqYYZBZCgVjdQvwgxVlDPOAfeUE5QjaGck4RFwFw8X0acFnBE5F67Yhj5oJlbFIeEG1ZACMxkH8LqkIb5P5hrNVBUZB5FxBdNeVDEwZCKLqIhPkZD'
                        # ans = sendWAMessage(phone, message, token)
                        string_test = Sender.objects.get(phone_number_id='15551289039')
                        token = string_test.access_token
                        
                        headers = {"Authorization": token}
                        payload = {
                                  "messaging_product": "whatsapp",
                                  "recipient_type": "individual",
                                  "to": str(fromID),
                                  "type": "text",
                                  "text": {"body":'RE: {} was received {},{}'.format(text,fromID,phoneNumber)}  
                                   }
                        respone = requests.post(settings.WHATSAPP_URL, headers=headers, json=payload)
                        ans = respone.json()
                        print(ans)


                except:
                    pass

        return HttpResponse('success', status=200)
    
   
# def home(request):
    
#     # load data records
#     records = Record.objects.all()
#     group_records = Group_Record.objects.all()
#     sender_records = Sender.objects.all()
    
    
    
#     # check login
#     if request.method == 'POST':
#         username = request.POST["username"]
#         password = request.POST["password"]
        
#         # Authenticate
#         user = authenticate(request, username=username, password=password)
#         if user is not None:
#             login(request, user)
#             messages.success(request, "Logged In")
#             return redirect('home')
#         else:
#             messages.success(request, "Error Login...")
#             return redirect('home')
#     else:          
#         return render(request, 'home.html', {'records': records, 'group_records': group_records, 'sender_records': sender_records})


    

def getTokens(code):
    TOKEN_ENDPOINT = settings.TOKEN_ENDPOINT
    
    CLIENT_ID = settings.CLIENT_ID
    CLIENT_SECRET = settings.CLIENT_SECRET
    REGION = settings.COGNITO_REGION_NAME
    USERPOOL_ID = settings.USER_POOL_ID

    token_1 = code[1: ]
    token_2 = token_1[:-1]
    print(token_2)
    claims = jwt_sync.decode(token_2, REGION, USERPOOL_ID)
    print(claims)

    if not claims:
        return False
    
    user = {
        'id_token': token_2,
        'name': claims['cognito:username'],
        'email': claims['email']
    }
    return user

def getSession(request):
    try:
        response = request.COOKIES["sessiontoken"]
        return response
    except:
        return None

def home(request):
    
    if 'userlogged' in request.session:
        print('yes')
    else:
        print('no')
    #status_1 = request.session['userlogged']
    #print(status_1)

    return render(request, 'home.html')

def test(request):
    return render(request, 'test.html')


@csrf_exempt
def home1(request):  

    current ={}
    
    if request.method == 'POST':
        try:
            request_getdata = request.POST.get('getdata', None)
            #print(request_getdata)
            userData = getTokens(request_getdata)
            #print(userData)
            current['name'] = userData['name']
            current['status'] = 1

            response = render(request, 'home1.html', current)
            request.session['userlogged'] = True
            response.set_cookie('sessiontoken', userData['id_token'], max_age=60*60*24, httponly=True)

            status = request.COOKIES.get('status')
            print('home1',status)

            return response 
            #return redirect('test.html') 
        except:
            token = getSession(request)
            print(token)
            if token is not None:
                userData = jwt_sync.decode(token_2, REGION, USERPOOL_ID)
                current['name'] = userData['name']
                current['status'] = 1
                response =  render(request, 'home1.html', current)
                return response 
            else:
                messages.success(request, "Login First..")
                return render(request, 'home1.html', {'status':0})

        
       
        


        #userData = decode_jwt.lambda_handler(token_2,None)
        #print(userData)
        #user = authenticate(request, id_token=request_getdata)
        # if user:
        #     login(request, user)
        #     print('yes')
        # # # Redirect or respond accordingly upon successful authentication
        #     return HttpResponse('Authenticated')
        # else:
        # #     # Handle authentication failure
        #     print('no')
        #     return HttpResponse('Authentication failed')
        

   
    # if request.method == 'POST':

    #     token = json.loads(request.body)
    #     print('hahah')
    #     print (token)
    # else:
    #     print('yes')

        # #id_token = request.POST.get("id_token") # Get the ID token from the frontend
        # id_token = json.dumps(request.GET.get('tokendata'))
        # print(id_token)
        # user = authenticate(request, id_token=id_token)
        # print(user)

        # data = json.loads(request.body)
        # print(data)
        
           

        #messages.success(request, "Login First...")
    return render(request, 'home1.html')

    

def logout_user(request):
    try:
        del request.session['userlogged']
        messages.success(request, "Logged Out....")
    except keyError:
        pass
    return redirect('home')


def customer_record(request, pk):
    if request.user.is_authenticated:
        
        # lookup records
        customer_record = Record.objects.get(id=pk)
        chats = Communication_Record.objects.all()
        return render(request, 'record.html', {'customer_record': customer_record, 'chats':chats})
    
    else:
        messages.success(request, "Login First...")
        return redirect('home')
    

def  delete_customer_record(request, pk):
    if request.user.is_authenticated:
        
        #delete records
        delete_customer = Record.objects.get(id=pk)
        delete_customer.delete()
        messages.success(request, "Record Deleted...")
        return redirect('customer_record_management')
        
    else:
        messages.success(request, "Login First...")
        return redirect('home')
    
    
def  add_customer_record(request):
    if request.user.is_authenticated:
        
        form = AddRecordForm(request.POST or None)

        if request.method == "POST":
            data = request.POST.copy()
            _muatble = data._mutable
            data._mutable = True
            
            phone = request.POST.get('phone')
            phone_str=str(phone)
            
            if len(phone_str) == 10 and phone_str[0] == '0':
                new_phone_str =  '61' + phone_str[1:] 
                print(new_phone_str)
                data['phone'] = new_phone_str
                data._mutable = _muatble
            elif len(phone_str) == 9:
                new_phone_str =  '61' + phone_str 
                print(new_phone_str)
                data['phone'] = new_phone_str
                data._mutable = _muatble
        
            form = AddRecordForm(data)
            phone = request.POST.get('phone')
            email = request.POST.get('email')
            verify_phone_exists = Record.objects.filter(phone=str(data['phone'])).exists()
            
            if form.is_valid():
                is_au_mobile = validate_au_mobile(phone)
                is_email_address_valid = is_email_valid(email)
                #print(is_au_mobile, is_email_address_valid)
                
                if is_au_mobile == True and is_email_address_valid == True and verify_phone_exists == False:
                    add_customer_record = form.save(commit=False)
                    if Record.objects.filter(phone=str(add_customer_record.phone)).exists() == False:
                        add_customer_record.save()
                        messages.success(request, "New Customer Infor Added...")
                        return redirect('home')
                    else:
                        messages.success(request, "Phone Number Existed in Database")
                        
                elif verify_phone_exists:
                    messages.success(request, "Phone Number Existed in Database")
                elif is_au_mobile == False:
                    messages.success(request, "Incorrect Phone Number")
                elif is_email_address_valid == False:
                    messages.success(request, "Incorrect Email Address")
                else:
                    messages.success(request, "Incorrect Phone Number and Email Address")
        
        return render(request, 'add_customer_record.html', {'form':form})
        
    else:
        messages.success(request, "Login First...")
        return redirect('home')
    
    
    
def update_customer_record(request, pk):
    
    if request.user.is_authenticated:
            
        #delete records
        current_customer = Record.objects.get(id=pk)
        form = AddRecordForm(request.POST or None, instance=current_customer)
        
        if form.is_valid():
            phone = request.POST.get('phone')
            email = request.POST.get('email')
            
            #print(phone, email)
             
            is_au_mobile = validate_au_mobile(phone)
            is_email_address_valid = is_email_valid(email)
            verify_phone_exists = Record.objects.filter(phone=str(phone)).exists()
            
            if is_au_mobile == True and is_email_address_valid == True and verify_phone_exists == False:
                
                updateform = form.save(commit=False)
                
                phone_str=str(updateform.phone)
                if len(phone_str) == 10 and phone_str[0] == '0':
                    new_phone_str =  '61' + phone_str[1:] 
                    #print(new_phone_str)
                    updateform.phone = new_phone_str
                elif len(phone_str) == 9:
                    new_phone_str =  '61' + phone_str 
                    #print(new_phone_str)
                    updateform.phone = new_phone_str
                
                if Record.objects.filter(phone=str(updateform.phone)).exists() == False:
                    updateform.save()
                    messages.success(request, "Record Updated...")
                    return redirect('customer_record_management')
                else:
                    messages.success(request, "Phone Number Existed in Database")
                    
            elif verify_phone_exists:
                    messages.success(request, "Phone Number Existed in Database")
            elif is_au_mobile == False:
                messages.success(request, "Incorrect Phone Number")
            elif is_email_address_valid == False:
                messages.success(request, "Incorrect Email Address")
            else:
                messages.success(request, "Incorrect Phone Number and Email Address")
        
        return render(request, 'update_customer_record.html', {'form':form})
    
    else:
        messages.success(request, "Login First...")
        return redirect('home')
    

def group_record(request, pk):
    if request.user.is_authenticated:
        
        # lookup records
        group_member_record = Group_Record.objects.get(id=pk)
        group_chats = Group_Communication_Record.objects.all()
        return render(request, 'group_record.html', {'group_member_record': group_member_record, 'group_chats':group_chats })
    
    else:
        messages.success(request, "Login First...")
        return redirect('home')
    

def  delete_group_record(request, pk):
    if request.user.is_authenticated:
        
        #delete records
        delete_group = Group_Record.objects.get(id=pk)
        delete_group.delete()
        messages.success(request, "Group Deleted...")
        return redirect('group_record_management')
        
    else:
        messages.success(request, "Login First...")
        return redirect('home')
    
    
def  add_group_record(request):
    if request.user.is_authenticated:
        
        form = AddGroupForm(request.POST or None)
        
        if request.method == "POST":
            if form.is_valid():
                add_group_record = form.save()
                messages.success(request, "New Group Created...")
                return redirect('home')
        
        return render(request, 'add_group_record.html', {'form':form})
        
    else:
        messages.success(request, "Login First...")
        return redirect('home')
    
    
def update_group_record(request, pk):
    
    if request.user.is_authenticated:
            
        #delete records
        current_group = Group_Record.objects.get(id=pk)
        form = AddGroupForm(request.POST or None, instance=current_group)
        
        if form.is_valid():
            form.save()
            messages.success(request, "Group Updated...")
            return redirect('group_record_management')
        
        return render(request, 'update_group_record.html', {'form':form})
    
    else:
        messages.success(request, "Login First...")
        return redirect('home')
    
    
def sender_record(request, pk):
    if request.user.is_authenticated:
            
        #delete records
        sender_record = Sender.objects.get(id=pk)
        return render(request, 'sender.html', {'sender_record':sender_record})
    
    else:
        messages.success(request, "Login First...")
        return redirect('home')
    

def  delete_sender_record(request, pk):
    if request.user.is_authenticated:
        
        #delete records
        delete_sender_record = Sender.objects.get(id=pk)
        delete_sender_record.delete()
        messages.success(request, "Group Deleted...")
        return redirect('sender_record_management')
        
    else:
        messages.success(request, "Login First...")
        return redirect('home')
    
    
def  add_sender_record(request):
    if request.user.is_authenticated:
        
        form = AddSenderForm(request.POST or None)
        
        
        if request.method == "POST":
            if form.is_valid():
                
                phone_number_id = request.POST.get('phone_number_id')
                print(phone_number_id)
                #is_mobile = validate_phone(phone_number_id)
                verify_sender_exists = Sender.objects.filter(phone_number_id=str(phone_number_id)).exists()
                #print(is_mobile)
                #if is_mobile == True and verify_sender_exists == False:
                if verify_sender_exists == False:
                    add_sneder_record = form.save()
                    messages.success(request, "New Sender Created...")
                    return redirect('home')
                else:
                    messages.success(request, "Sender Exist...")
        
        return render(request, 'add_sender_record.html', {'form':form})
        
    else:
        messages.success(request, "Login First...")
        return redirect('home')
    
    
def update_sender_record(request, pk):
    
    if request.user.is_authenticated:
            
        #delete records
        current_group = Sender.objects.get(id=pk)
        form = AddSenderForm(request.POST or None, instance=current_group)
        
        if form.is_valid():
            
            update_sender = form.save(commit=False)
            
            #verify_sender_exists = Sender.objects.filter(phone_number_id=str(update_sender.phone_number_id)).exists()
            
            #if verify_sender_exists == False:
                #update_sender.save()
                #messages.success(request, "Sender Updated...")
                #return redirect('home')
            #else:
                #messages.success(request, "Sender Exist...")
            update_sender.save()
            messages.success(request, "Sender Updated...")
            return redirect('sender_record_management')
        
        return render(request, 'update_sender_record.html', {'form':form})
    
    else:
        messages.success(request, "Login First...")
        return redirect('home')
    
def sendMessageIndividual(request):
    
    if request.user.is_authenticated:
        
        form = ChatMessageForm(request.POST or None)
        
        #sender = Sender.objects.get(id=request.POST.get('sender'))
        #receiver = Record.objects.get(id=request.POST.get('contact'))
        #sender = request.POST.get('sender')
        #receiver = request.POST.get('contact')
        
        if request.method == "POST":
            if form.is_valid():
                new_message = form.save(commit=False)
                new_message.sender = Sender.objects.get(id=request.POST.get('sender'))
                new_message.contact = Record.objects.get(id=request.POST.get('contact'))
                
                token = new_message.sender.access_token
                phone = new_message.contact.phone
                message = new_message.message_text
                ans = sendWAMessage(phone, message, token)
                
                if ans == True:
                    new_message.status = 'sent'
                    new_message.send_method = 'individual messages'
                    new_message.save()
                    messages.success(request, "New Message send...")
                    return redirect('home')
                else:
                    new_message.status = 'error'
                    new_message.send_method = 'Individual Message'
                    new_message.save()
                    messages.success(request, "Error...")
                    return redirect('home')
        
        return render(request, 'sendMessageIndividual.html', {'form':form})
    
    else:
        messages.success(request, "Login First...")
        return redirect('home')

def sendGroupMessageIndividual(request):
    
    form = ChatGroupMessageForm(request.POST or None)
    
    if request.user.is_authenticated:
        
        if request.method == "POST":
            if form.is_valid():
                new_group_message = form.save(commit=False)
                new_group_message.sender = Sender.objects.get(id=request.POST.get('sender'))
                new_group_message.group = Group_Record.objects.get(id=request.POST.get('group'))
                
                print(new_group_message.group.user.all())
                print(new_group_message.group_message_text)
                
               
                group_status = []
                for individual_object in new_group_message.group.user.all():
                    individual_message = Communication_Record.objects.create(
                    sender = new_group_message.sender,
                    contact = individual_object,
                    message_text = new_group_message.group_message_text,
                    )

                    token = new_group_message.sender.access_token
                    phone = individual_object.phone
                    message = new_group_message.group_message_text
                    ans = sendWAMessage(phone, message, token)

                    if ans == True:
                        group_status.append([phone, individual_message.status])
                        individual_message.status = 'sent'
                        individual_message.send_method = 'Group Messages'
                        individual_message.save()
                   
                    
                    else:
                        group_status.append([phone, individual_message.status])
                        individual_message.status = 'error'
                        individual_message.send_method = 'group messages'
                        individual_message.save()
                  
                new_group_message.group_status = group_status
                new_group_message.send_method = 'group messages'
                new_group_message.save()
               
                messages.success(request, "New Group Message send...")
                return redirect('home')
        
        return render(request, 'sendGroupMessageIndividual.html', {'form':form})
    
    else:
        messages.success(request, "Login First...")
        return redirect('home')
    
def customer_record_management(request):
    # load data records
    
    # get search from url
    data_dict ={}
    search_value = request.GET.get('search',"")
    
    if search_value:
        data_dict["phone__contains"]=search_value
     
    # get page_object to split page
    search = Record.objects.filter(**data_dict)
    
    # get page_object to split page
    page_object = Pagination(request, search)
    
    context = {
            'search_value':search_value,
            'records': page_object.search, 
            "page_string": page_object.html()
               }
    
    # check login
    if request.method == 'POST':
        username = request.POST["username"]
        password = request.POST["password"]
        
        # Authenticate
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Logged In")
            return redirect('home')
        else:
            messages.success(request, "Error Login...")
            return redirect('home')
    else:          
        return render(request, 'manage_customer.html', context)

def group_record_management(request):
    
     # get search from url
    data_dict ={}
    search_value = request.GET.get('search',"")
    
    if search_value:
        data_dict["group_name__contains"]=search_value
     
    # get page_object to split page
    search = Group_Record.objects.filter(**data_dict)
    
    # get page_object to split page
    page_object = Pagination(request, search)
    
    context = {
            'search_value':search_value,
            'group_records': page_object.search, 
            "page_string": page_object.html()
               }

    
    # check login
    if request.method == 'POST':
        username = request.POST["username"]
        password = request.POST["password"]
        
        # Authenticate
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Logged In")
            return redirect('home')
        else:
            messages.success(request, "Error Login...")
            return redirect('home')
    else:          
        return render(request, 'manage_group.html', context )

def sender_record_management(request):
    

     # get search from url
    data_dict ={}
    search_value = request.GET.get('search',"")
    
    if search_value:
        data_dict["phone_number_id__contains"]=search_value
    
    # get page_object to split page
    search = Sender.objects.filter(**data_dict)
    
    # get page_object to split page
    page_object = Pagination(request, search)
    
    context = {
            'search_value':search_value,
            'sender_records': page_object.search, 
            "page_string": page_object.html()
               }
    
    # check login
    if request.method == 'POST':
        username = request.POST["username"]
        password = request.POST["password"]
        
        # Authenticate
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Logged In")
            return redirect('home')
        else:
            messages.success(request, "Error Login...")
            return redirect('home')
    else:          
        return render(request, 'manage_sender.html', context)
    
def customer_page(request):
    
    if request.user.is_authenticated:
        
        # lookup records
        customer_record = Record.objects.all()
        chats = Communication_Record.objects.all()
        
        # all customer
        customer_str_list = []
        for i in customer_record:
            name = str(i.first_name) + ' ' + str(i.last_name)
            id = i.contact_id
            element ='<div class="chat-user"><img class="chat-avatar" src="" alt=""><div class="chat-user-name"><a href="?ID={}">{}</a></div></div>'.format(id, name)
            customer_str_list.append(element)
            
        customer_string = mark_safe("".join(customer_str_list))
        
        # all chats
        chat_str_list = []
        chat_onwer_id = request.GET.get("ID")
        for i in chats:
            author = i.contact
            time = i.sent_datetime
            message = i.message_text
            status = i.status
            if status == 'sent':
                chat_status = 'left'
                color = '#00FFFF'
            elif status == 'received':
                chat_status = 'right'
                color = '#F5F5DC'
            else:
                chat_status = 'left'
                color ='#DC143C'
                
            if i.contact.contact_id == chat_onwer_id:
                chat_element = '<div class="chat-message {}"><img class="message-avatar" src="https://bootdey.com/img/Content/avatar/avatar1.png" alt=""><div class="message" style="background:{}"><a class="message-author" href="#">{}</a><span class="message-date">{}</span><span class="message-content">{}</span></div></div>'.format(chat_status, color, author, time, message)
                chat_str_list.append(chat_element)
                
        chat_srting = mark_safe("".join(chat_str_list))
            #== customer_record.id or chat.sender.id == customer_record.id
        
        
        return render(request, 'customer_page.html', {'customer_string':customer_string, 'chat_srting':chat_srting})
    
    else:
        messages.success(request, "Login First...")
        return redirect('home') 

def group_page(request):
    
    if request.user.is_authenticated:
        
        # lookup records
        group_record = Group_Record.objects.all()
        chats = Group_Communication_Record.objects.all()
        
        # all customer
        customer_str_list = []
        for i in group_record:
            name = i.group_name
            id = i.group_id
            element ='<div class="chat-user"><img class="chat-avatar" src="" alt=""><div class="chat-user-name"><a href="?ID={}">{}</a></div></div>'.format(id, name)
            customer_str_list.append(element)
            
        customer_string = mark_safe("".join(customer_str_list))
        
        # all chats
        chat_str_list = []
        chat_group_onwer_id = request.GET.get("ID")
        for i in chats:
            author = i.group
            time = i.group_sent_datetime
            message = i.group_message_text
            status = i.group_status
            if status == 'sent':
                chat_status = 'left'
                color = '#00FFFF'
            elif status == 'received':
                chat_status = 'right'
                color = '#F5F5DC'
            else:
                chat_status = 'left'
                color ='#DC143C'
                
            if i.group.group_id == chat_group_onwer_id:
                chat_element = '<div class="chat-message {}"><img class="message-avatar" src="https://bootdey.com/img/Content/avatar/avatar1.png" alt=""><div class="message" style="background:{}"><a class="message-author" href="#">{}</a><span class="message-date">{}</span><span class="message-content">{}</span></div></div>'.format(chat_status, color, author, time, message)
                chat_str_list.append(chat_element)
                
        chat_srting = mark_safe("".join(chat_str_list))
            #== customer_record.id or chat.sender.id == customer_record.id
        
        
        return render(request, 'group_page.html', {'customer_string':customer_string, 'chat_srting':chat_srting})
    
    else:
        messages.success(request, "Login First...")
        return redirect('home') 