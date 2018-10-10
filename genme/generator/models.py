from django.db import models

# Create your models here.
class Categories(models.Model):
    id = models.IntegerField(primary_key=True)
    categories = models.CharField(max_length=500)

class TrainingStatus(models.Model):
    id = models.IntegerField(primary_key=True)
    status = models.CharField(max_length=200)