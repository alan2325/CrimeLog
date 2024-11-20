from django.db import models


class User(models.Model):
    Email = models.EmailField(unique=True)
    username = models.TextField()
    phonenumber = models.IntegerField()
    password = models.TextField()
    location= models.TextField()
    idproof= models.FileField()

    def __str__(self):
        return self.username

class Police(models.Model):
    Email = models.EmailField(unique=True)
    name = models.TextField()
    # phonenumber = models.IntegerField()
    password = models.TextField()
    # location= models.TextField()
 

    def __str__(self):
        return self.name
    


class Complaint(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link complaint to the user
    police = models.ForeignKey(Police, on_delete=models.CASCADE)  # Link complaint to a police officer
    subject = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=50, choices=[('Pending', 'Pending'), ('Resolved', 'Resolved')], default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Complaint by {self.user.username} - {self.subject}"
