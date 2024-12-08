from django.shortcuts import render,redirect,get_object_or_404
from .models import *
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import User
from django.contrib import messages
import re
from django.core.files.storage import default_storage
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required


# from django.contrib.auth.decorators import login_required

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
        return redirect(view_complaints)

    if req.method == 'POST':
        email = req.POST['Email']
        password = req.POST['password']
        
        # Check if it's an admin login
        admin_user = authenticate(username=email, password=password)
        if admin_user and admin_user.is_superuser:
            auth_login(req, admin_user)
            return redirect(viewcomplaint)

        # Handle normal user login
        try:
            user = User.objects.get(Email=email, password=password)
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
    if req.user.is_authenticated:
        auth_logout(req)  # Logout for admin users
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
        police_id = 123 
        complaint = Complaint.objects.filter().order_by('-created_at') 
        return render(req,'user/home.html',{'complaint':complaint,'police_id': police_id})
    else:
        return redirect(login)
    
def aboutus(req):
    return render(req,'user/about.html')

# def usersearch(req):
#     if 'user' in req.session:
#         query = req.GET.get('query') 
#         products = []
#         if query:
#             products = User.objects.filter(name__icontains=query)
            
#         return render(req, 'user/usersearch.html', {'products': products, 'query': query})
#     else:
#         return redirect(login)
    


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
    

def userhistory(req):
    if 'user' in req.session:
        user = get_user(req)  
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
    
def viewpolices(req):
    
        data=Police.objects.all()
        return render(req,'user/viewpolice.html', {'data':data})
    



def policesearch(request):
    query = request.POST.get('query')  # Get the search term from the request
    police = []
    if query:
        police = Police.objects.filter(name=query)
        
    return render(request, 'user/policesearch.html', {'police': police, 'query': query})

    
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

def usersearch(request):
    query = request.POST.get('query')  # Get the search term from the request
    user = []
    if query:
        user = User.objects.filter(username=query)
        
    return render(request, 'police/usersearch.html', {'user': user, 'query': query})


def viewuser(req):
    
        data=User.objects.all()
        return render(req,'police/viewuser.html', {'data':data})
    


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




@login_required
def adminhome(req):
    if not req.user.is_superuser:
        return redirect(login)
    data=Complaint.objects.all()
    return render(req,'admin/viewcomplaint.html',{'data':data})

@login_required
def viewusers(req):
    if not req.user.is_superuser:
        return redirect(login)
    data = User.objects.all()
    return render(req, 'admin/viewusers.html', {'data': data})

def adminhome(req):
    return render(req,'admin/adminhome.html')

def viewpolice(req):
    data=Police.objects.all()
    return render(req,'admin/viewpolice.html',{'data':data})

# def viewusers(req):
#     data=User.objects.all()
#     return render(req,'admin/viewusers.html',{'data':data})

def viewcomplaint(req):
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




###Ask Anything
def message(req):
    if 'user' in req.session:  # Check if the user is logged in
        user_email = req.session.get('user')  # Get the user's email from the session
        user = User.objects.get(Email=user_email)  # Retrieve the user object using email
        
        police_officers = Police.objects.all()  # Fetch all police officers

        # Fetch all messages where the user or police is involved
        data1 = Chat.objects.filter(user=user).order_by('id')

        if req.method == 'POST':
            msg = req.POST.get('content')  # Get the message content
            police_id = req.POST.get('police_id')  # Get the police officer's ID
            if msg and police_id:
                police = Police.objects.get(pk=police_id)  # Retrieve the police officer
                # Create a new chat message
                Chat.objects.create(user=user, police=police, content=msg)

        return render(req, 'user/message.html', {
            'data1': data1,
            'police_officers': police_officers,
        })
    else:
        return redirect('login')  # Redirect to login if the user is not logged in




def messagee(req):
    if 'police' in req.session:  # Check if the police officer is logged in
        police_email = req.session.get('police')  # Get the police officer's email from the session
        police = Police.objects.get(Email=police_email)  # Retrieve the police object
        
        # Fetch all messages where the police officer or user is involved
        data1 = Chat.objects.filter(police=police).order_by('id')

        if req.method == 'POST':
            msg = req.POST.get('content')  # Get the message content
            user_id = req.POST.get('user_id')  # Get the user's ID from the form
            if msg and user_id:
                user = User.objects.get(pk=user_id)  # Retrieve the user object
                # Create a new chat message
                Chat.objects.create(police=police, user=user, content=msg)

        return render(req, 'police/messagee.html', {
            'data1': data1,
        })
    else:
        return redirect('login')  # Redirect to login if the police officer is not logged in
