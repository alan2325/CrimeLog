from django.db import models


class User(models.Model):
    Email = models.EmailField(unique=True)
    username = models.TextField()
    phonenumber = models.IntegerField()
    password = models.TextField()
    location = models.TextField()
    idproof = models.FileField()
    profile_picture = models.ImageField(upload_to='profile_pics/', default='profile_pics/default.png')  # Ensure the default image is in the correct path.

    def __str__(self):
        return self.username

class Police(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    Email = models.EmailField(unique=True)
    name = models.TextField()
    # phonenumber = models.IntegerField()
    password = models.TextField()
    # location= models.TextField()
 

    def __str__(self):
        return self.name
    


class Complaint(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    police = models.ForeignKey(Police, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=50, choices=[('Pending', 'Pending'), ('Registered', 'Registered'), ('Resolved', 'Resolved')], default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    registered_at = models.DateTimeField(null=True, blank=True)  # Optional

    def __str__(self):
        return f"Complaint by {self.user.username} - {self.subject}"
    
class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"From {self.sender.username} to {self.receiver.username}"
