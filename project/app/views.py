from django.shortcuts import render,redirect
from .models import *
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib import messages
import re


# Create your views here.

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
    

    if req.method=='POST':
        Email=req.POST['Email']
        password=req.POST['password']
        try:
            data=User.objects.get(Email=Email,password=password)
            req.session['user']=data.Email
            return redirect(userhome)
        except User.DoesNotExist:
            data=Police.objects.get(Email=Email,password=password)
            req.session['police']=data.Email

            return redirect(policehome)
    else:
        messages.warning(req, "INVALID INPUT !")
    return render(req,'login.html')
    

def logout(req):
    if 'user' in req.session:
        del req.session['user']
    if 'police' in req.session:
        del req.session['police']
    return redirect(login)


def user_reg(req):

    if req.method=='POST':
        name=req.POST['username']
        email=req.POST['Email']
        phonenumber=req.POST['phonenumber']
        location=req.POST['location']
        password=req.POST['password']
         # Validate email
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
            return redirect(login)
        except:
            messages.warning(req, "Email Already Exits , Try Another Email.")
    return render(req,'user/user_reg.html')


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


def userhome(req):
    if 'user' in req.session:
        return render(req,'user/home.html')
    
def policehome(req):
    if 'police' in req.session:
        return render(req,'police/home.html')
    
def usersearch(request):
    query = request.GET.get('query') 
    products = []
    if query:
        products = User.objects.filter(name__icontains=query)
        
    return render(request, 'user/usersearch.html', {'products': products, 'query': query})


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


def view_complaints(req):
    if 'police' not in req.session:
        return redirect(login)  # Ensure police is logged in

    police = get_police(req)
    complaints = Complaint.objects.filter(police=police).order_by('-created_at')
    return render(req, 'police/view_complaints.html', {'complaints': complaints})


######### user view profile

def userprofile(req):
    if 'user' in req.session:
        return render(req,'user/user_profile.html',{'data':get_user(req)})
    else:
        return redirect(login)
    

###profile update
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
            if not re.match(r'^[789]\d{9}$', phonenumber):
                return render(req, 'user/update_user_profile.html', {
                    'data': data,
                    'error_message': 'Invalid phone number'
                })
            User.objects.filter(Email=req.session['user']).update(username=name, phonenumber=phonenumber, location=location)
            return redirect(userprofile)
        return render(req, 'user/update_user_profile.html', {'data': data})

    else:

        return redirect(login)