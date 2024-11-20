from django.urls import path
from . import views
urlpatterns = [
path('',views.login),
path('logout',views.logout),
path('user_reg',views.user_reg),
path('userhome',views.userhome),
path('policehome',views.policehome),
path('usersearch/',views.usersearch, name='usersearch'),

    
]