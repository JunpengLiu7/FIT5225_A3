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
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.home, name='home'),
    path('upload_image/', views.upload_image, name='upload_image'),
    #path('login/', views.login_user, name='login'),
    # path('logout/', views.logout_user, name='logout'),
    # change the uil by add infornt
    
    
    # https://texting.alexxhometest.com/80e9f013-5924-4da0-aa6f-21d552f9e8ac
    # token: 4eee0753-2969-4c14-9bc7-387234169bc5

]
