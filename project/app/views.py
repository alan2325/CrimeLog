from django.shortcuts import render,redirect
from .models import *
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import User
from django.contrib import messages
import re
from django.core.files.storage import default_storage
from django.core.mail import send_mail
from django.conf import settings
# from django.contrib.auth.decorators import login_required
# from django.db.models import Q






def get_user(req):
    data=User.objects.get(Email=req.session['user'])
    return data

def get_police(req):
    data=Police.objects.get(Email=req.session['police'])
    return data

def login(req):
    if 'user' in req.session:
        return redirect(userhome)
    if 'police' in req.session:
        return redirect(policehome)
    
    if req.method == 'POST':
        email = req.POST['Email']  # Lowercase as per the custom model
        password = req.POST['password']
        try:
            user = User.objects.get(Email=email, password=password)  # Use custom model field names
            req.session['user'] = user.Email
            return redirect(userhome)
        except User.DoesNotExist:
            try:
                police = Police.objects.get(Email=email, password=password)
                req.session['police'] = police.Email
                return redirect(view_complaints)
            except Police.DoesNotExist:
                messages.warning(req, "Invalid email or password")
    return render(req, 'login.html')


def logout(req):
    if 'user' in req.session:
        del req.session['user']
    if 'police' in req.session:
        del req.session['police']
    return redirect(login)



#################  user  #######################

def user_reg(req):

    if req.method=='POST':
        name=req.POST['username']
        email=req.POST['Email']
        phonenumber=req.POST['phonenumber']
        location=req.POST['location']
        password=req.POST['password']
         
          
        try:
            validate_email(email)
        except ValidationError:
            messages.warning(req, "Invalid email format, please enter a valid email.")
            return render(req, 'user/user_reg.html')

        # Validate phone number (assuming 10-digit numeric format)
        if not re.match(r'^\d{10}$', phonenumber):
            messages.warning(req, "Invalid phone number. Please enter a valid 10-digit phone number.")
            return render(req, 'user/user_reg.html')
        try:
            data=User.objects.create(username=name,Email=email,phonenumber=phonenumber,location=location,password=password)
            data.save()
            # Validate email
            subject = 'Registration details '
            message = 'ur account uname {}  and password {}'.format(name,password)
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [email]
            send_mail(subject, message, from_email, recipient_list,fail_silently=False)
            return redirect(login)
        except:
            messages.warning(req, "Email Already Exits , Try Another Email.")
    return render(req,'user/user_reg.html')

def userhome(req):
    if 'user' in req.session:
        # user = get_user(req)
        complaint = Complaint.objects.filter().order_by('-created_at') 
        return render(req,'user/home.html',{'complaint':complaint})
    else:
        return redirect(login)
    

def usersearch(req):
    if 'user' in req.session:
        query = req.GET.get('query') 
        products = []
        if query:
            products = User.objects.filter(name__icontains=query)
            
        return render(req, 'user/usersearch.html', {'products': products, 'query': query})
    else:
        return redirect(login)
    


def submit_complaint(req):
    if 'user' not in req.session:
        return redirect(login)  # Ensure the user is logged in

    user = get_user(req)
    police_officers = Police.objects.all()  # Fetch all police officers for assignment

    if req.method == 'POST':
        subject = req.POST['subject']
        description = req.POST['description']
        police_id = req.POST.get('police')

        if not subject or not description or not police_id:
            messages.warning(req, "All fields are required!")
            return redirect(submit_complaint)

        police = Police.objects.get(id=police_id)
        complaint = Complaint.objects.create(
            user=user,
            police=police,
            subject=subject,
            description=description
        )
        complaint.save()
        messages.success(req, "Complaint submitted successfully.")
        return redirect(userhome)

    return render(req, 'user/submit_complaint.html', {'police_officers': police_officers})

######### user view profile

def userprofile(req):
    if 'user' in req.session:
        return render(req,'user/user_profile.html',{'data':get_user(req)})
    else:
        return redirect(login)
    

########## user profile update

def updateuserprofile(req):
    if 'user' in req.session:
        try:
            data = User.objects.get(Email=req.session['user'])
        except User.DoesNotExist:
            return redirect(login)

        if req.method == 'POST':
            name = req.POST['username']
            phonenumber = req.POST['phonenumber']
            location = req.POST['location']
            profile_picture = req.FILES.get('profile_picture')  # Handle the file upload

            # Validate phone number
            if not re.match(r'^[789]\d{9}$', phonenumber):
                return render(req, 'user/update_user_profile.html', {
                    'data': data,
                    'error_message': 'Invalid phone number'
                })

            # Update user details
            if profile_picture:  # Update only if a new file is uploaded
                picture_path = default_storage.save(profile_picture.name, profile_picture)
                data.profile_picture = picture_path
            data.username = name
            data.phonenumber = phonenumber
            data.location = location
            data.save()
            return redirect(userprofile)

        return render(req, 'user/update_user_profile.html', {'data': data})

    else:
        return redirect(login)
    
# def userhistory(req):
#     if 'user' in req.session:
#         data=User.objects.all()
#         return render(req,'user/user_history.html',{'data':data})
#     else:
#         return redirect(login)

def userhistory(req):
    if 'user' in req.session:
        user = get_user(req)  # Get the currently logged-in user
        complaints = Complaint.objects.filter(user=user).order_by('-created_at')  # Fetch complaints specific to this user
        return render(req, 'user/user_history.html', {'complaints': complaints})
    else:
        return redirect(login)

def chat(req,id):
    if 'user' in req.session:
        complaint=Complaint.objects.get(pk=id)
        data1 = Message.objects.filter(complaint=complaint)

        if req.method=='POST':
            msg=req.POST.get('content')
            if msg:
                data=Message.objects.create(complaint=complaint,content=msg)
                data.save()
        return render(req,'user/chat.html',{'data1':data1})
    else:
        return redirect(login) 

    
def contactus(req):
    if 'user' in req.session:
        data=Police.objects.all()
        return render(req, 'user/contact_us.html',{'data':data})
    else:
        return redirect(login)


################### police  ###############

def police_reg(req):
    if req.method=='POST':
        name=req.POST['name']
        email=req.POST['Email']
        password=req.POST['password']
         # Validate email
        try:
            validate_email(email)
        except ValidationError:
            messages.warning(req, "Invalid email format, please enter a valid email.")
            return render(req, 'police/police_reg.html')

        # Validate phone number (assuming 10-digit numeric format)
        try:
            data=Police.objects.create(name=name,Email=email,password=password)
            data.save()
            return redirect(login)
        except:
            messages.warning(req, "Email Already Exits , Try Another Email.")
    return render(req,'police/police_reg.html')
    
def policehome(req):
    if 'police' in req.session:
        return render(req,'police/home.html')
    else:
        return redirect(login)

def view_complaints(req):
    if 'police' not in req.session:
        return redirect(login)  # Ensure the police officer is logged in

    police = get_police(req)  # Helper function to fetch police officer details
    complaints = Complaint.objects.filter(police=police).order_by('-created_at')

    if req.method == 'POST':
        complaint_id = req.POST.get('complaint_id')
        new_status = req.POST.get('status')

        try:
            complaint = Complaint.objects.get(id=complaint_id, police=police)
            complaint.status = new_status
            complaint.save()
            success_message = "Complaint status updated successfully."
        except Complaint.DoesNotExist:
            error_message = "Complaint not found or unauthorized action."

        return render(req, 'police/view_complaints.html', {
            'complaints': complaints,
            'success_message': success_message if 'success_message' in locals() else None,
            'error_message': error_message if 'error_message' in locals() else None,
        })

    return render(req, 'police/view_complaints.html', {'complaints': complaints})

def delete(req,id):
    data=Complaint.objects.get(pk=id)
    data.delete()
    return redirect(policehome) 

def viewuser(req):
    # if 'police' not in req.session:
        data=User.objects.all()
        return render(req,'police/viewuser.html', {'data':data})
    # else:
    #     return redirect(login)

# def registered_complaints(request):
#     if request.user.is_staff:  # If the user is a police/admin
#         complaints = Complaint.objects.all()
#     else:  # If the user is a general user
#         complaints = Complaint.objects.filter(user=request.user)

#     return render(request, "complaint_history.html", {"complaints": complaints})    
# 

def registered_complaints(req):
    if 'police' in req.session:
        police = get_police(req)
        complaints = Complaint.objects.filter(police=police)
    elif 'user' in req.session:
        user = get_user(req)
        complaints = Complaint.objects.filter(user=user)
    else:
        return redirect(login)

    return render(req, 'police/complaint_history.html', {'complaints': complaints})   



def chats(req, id):
    complaint = Complaint.objects.get(pk=id)
    data1 = Message.objects.filter(complaint=complaint)
    
    if req.method == 'POST':
        msg = req.POST.get('content')
        if msg:
            data = Message.objects.create(complaint=complaint, content=msg)
            data.save()
    
    return render(req, 'police/chats.html', {'data1': data1})



##################  admin ###############


def adminhome(req):
    return render(req,'admin/adminhome.html')

def viewpolice(req):
    data=Police.objects.all()
    return render(req,'admin/viewpolice.html',{'data':data})

def viewusers(req):
    data=User.objects.all()
    return render(req,'admin/viewusers.html',{'data':data})

def  viewcomplaint(req):
    data=Complaint.objects.all()
    return render(req,'admin/viewcomplaint.html',{'data':data})

def addstation(req):
    if req.method=='POST':
        name = req.POST['name']
        Email = req.POST['Email']
        password = req.POST['password']
        data=Police.objects.create(name=name,Email=Email,password=password)
        data.save()
        return redirect(viewpolice)
    return render(req,'admin/addstation.html')



# @login_required
def userchat_box(request):
    """Handles chat between user and police"""
    # police = Police.objects.get(id=police_id)
    # chats = Chat.objects.filter(police=police, user=request.user).order_by('timestamp')

    if request.method == 'POST':
        content = request.POST.get('content')
        if content.strip():  # Basic validation to ensure content is not empty
            Chat.objects.create(
                # police=police,
                user=request.user,
                content=content
            )
        return redirect(userchat_box)

    return render(request, 'user/chat_box.html', {
        'chats': chats,
        # 'police': police,
        'is_police': False,
    })


# @login_required
def police_chat_box(request):
    """Handles chat from the police perspective"""
    # user = User.objects.get(id=user_id)
    # police = Police.objects.get(user=request.user)  # Assuming Police is linked to User
    # chats = Chat.objects.filter(police=police).order_by('timestamp')

    if request.method == 'POST':
        content = request.POST.get('content')
        if content.strip():  # Basic validation to ensure content is not empty
            Chat.objects.create(
                # police=police,
                # user=user,
                content=content
            )
        return redirect('police_chat_box')

    return render(request, 'police/chat_box.html', {
        'chats': chats,
        # 'police': police,
        'is_police': True,
    })