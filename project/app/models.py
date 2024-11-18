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
    # Email = models.EmailField(unique=True)
    name = models.TextField()
    # phonenumber = models.IntegerField()
    password = models.TextField()
    # location= models.TextField()
 

    def __str__(self):
        return self.name
    