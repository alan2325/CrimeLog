from django.urls import path
from . import views
urlpatterns = [
path('',views.login),
path('logout',views.logout),

#### user

path('user_reg',views.user_reg),
path('userhome',views.userhome),
path('usersearch/',views.usersearch, name='usersearch'),
path('submit_complaint/', views.submit_complaint, name='submit_complaint'),
path('updateuserprofile',views.updateuserprofile),
path('userprofile',views.userprofile),


#### police 

path('police_reg',views.police_reg),
path('policehome',views.policehome),
path('view_complaints/', views.view_complaints, name='view_complaints'),
    
]