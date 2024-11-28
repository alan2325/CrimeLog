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
path('userprofile',views.userprofile),
path('updateuserprofile',views.updateuserprofile),
path('userhistory',views.userhistory),
path('chat/<int:id>', views.chat, name='chat'),




#### police 

path('police_reg',views.police_reg),
path('policehome',views.policehome),
path('view_complaints/', views.view_complaints, name='view_complaints'),
path('viewuser',views.viewuser),
path("complainthistory/", views.registered_complaints, name="complainthistory"),
path('delete/<int:id>',views.delete),
path('chats/<int:id>', views.chats, name='chats'),

# path('deleteitem/<int:id>',views.deleteitem),

 path('userchat/', views.userchat_box, name='chat_box'),  # For user
path('policechat/', views.police_chat_box, name='police_chat_box'), 



#### Admin

path('adminhome',views.adminhome),
path('viewpolice',views.viewpolice),
path('viewusers',views.viewusers),
path('viewcomplaint',views.viewcomplaint),


    
]