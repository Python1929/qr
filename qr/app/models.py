from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date

# Create your models here.

class Staff(models.Model):
    staffname = models.CharField(max_length=100)
    staffid = models.CharField(max_length=100)
    desgination = models.CharField(max_length=100)
    mailid = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    address = models.CharField(max_length=100)

    class Meta:
        db_table='staff'

class Contractor(models.Model):
    contractorname = models.CharField(max_length=100)
    contractorid = models.CharField(max_length=100)
    companyname = models.CharField(max_length=100)
    mailid = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    qrimage = models.CharField(max_length=100,default="null")

    class Meta:
        db_table='contractor'

class Visitor(models.Model):
    visitorname = models.CharField(max_length=100)
    mailid = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    purpose = models.CharField(max_length=100,null=True)
    qrimage = models.CharField(max_length=100,default="null")
    class Meta:
        db_table='visitor'

class EntryExit(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    intime = models.TimeField(default=timezone.now)
    date = models.DateField(default=date.today)
    class Meta:
        db_table = 'entryexit'

        


