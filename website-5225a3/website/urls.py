"""
URL configuration for whatsapptexting project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('home1/', views.home1, name='home1'),
    path('test/', views.test, name='test'),
    #path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    # change the uil by add infornt
    path('80e9f013-5924-4da0-aa6f-21d552f9e8ac', views.whatsAppWebhook, name='whatsapp-webhook'),
    
    # https://texting.alexxhometest.com/80e9f013-5924-4da0-aa6f-21d552f9e8ac
    # token: 4eee0753-2969-4c14-9bc7-387234169bc5

    path('home1/record/<int:pk>', views.customer_record, name='record'),
    path('delete_customer_record/<int:pk>', views.delete_customer_record, name='delete_customer_record'),
    path('add_customer_record/', views.add_customer_record, name='add_customer_record'),
    path('update_customer_record/<int:pk>', views.update_customer_record, name='update_customer_record'),
    
    path('group_record/<int:pk>', views.group_record, name='group_record'),
    path('delete_group_record/<int:pk>', views.delete_group_record, name='delete_group_record'),
    path('add_group_record/', views.add_group_record, name='add_group_record'),
    path('update_group_record/<int:pk>', views.update_group_record, name='update_group_record'),
    
    path('sender_record/<int:pk>', views.sender_record, name='sender_record'),
    path('delete_sender_record/<int:pk>', views.delete_sender_record, name='delete_sender_record'),
    path('add_sender_record/', views.add_sender_record, name='add_sender_record'),
    path('update_sender_record/<int:pk>', views.update_sender_record, name='update_sender_record'),
    
    path('sendMessageIndividual', views.sendMessageIndividual, name='sendMessageIndividual'),
    
    path('sendGroupMessageIndividual', views.sendGroupMessageIndividual, name='sendGroupMessageIndividual'),
    
    
    path('customer_record_management', views.customer_record_management, name='customer_record_management'),
    path('group_record_management', views.group_record_management, name='group_record_management'),
    path('sender_record_management', views.sender_record_management, name='sender_record_management'),
    
    path('customer_page', views.customer_page, name='customer_page'),
    path('group_page', views.group_page, name='group_page'),
]
