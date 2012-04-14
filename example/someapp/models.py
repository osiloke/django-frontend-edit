from django.db import models

# Create your models here.

class MyModel(models.Model):
	# This is just an example model
	text = models.TextField()
	name = models.CharField(max_length=255)