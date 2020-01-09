from django.db import models


# Create your models here.
class u1(models.Field):
    uid = models.AutoField(primary_key=True)
    uname = models.CharField(max_length=32)
    class Meta:
        managed = False
        db_table = 'u1'


# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=50)
    email = models.CharField(max_length=60)
    sex = models.CharField(max_length=60)
    birthday = models.CharField(max_length=60)
    password = models.CharField(max_length=20)

class movie(models.Model):
    id = models.CharField(max_length=12,primary_key=True)
    mname = models.CharField(max_length=60)
    mtype = models.CharField(max_length=60)
    myear = models.CharField(max_length=60)
    mename = models.CharField(max_length=60)
    mdirector = models.CharField(max_length=20)
    mrating = models.CharField(max_length=12)
    mjs = models.CharField(max_length=1024)
    mpicture = models.CharField(max_length=1024)
