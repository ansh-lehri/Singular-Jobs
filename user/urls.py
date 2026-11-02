from django.urls import path
from django.conf.urls import url, include

from user.views import user_reg
from user.views import user_login
from user.views import redirect_page
from user.views import user_profile
from user.views import change_password
from user.views import logout
from user.views import landing
from user.views import my_jobs
from user.views import faq

urlpatterns = [
    path('',landing,name="singular-jobs"),
    path('register',user_reg,name="register"),
    path('login',user_login,name="login"),
    path('redirect',redirect_page,name="redirecting"),
    path('profile',user_profile,name='profile'),
    path('change_password',change_password,name='change_password'),
    path('logout',logout,name='logout'),
    path('my_jobs',my_jobs,name='my_jobs'),
    path('faq',faq,name='faq'),
]

