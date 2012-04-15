from django.db import models

# Create your models here.

class TodoItem(models.Model):
	# This is just an example todo model
	text = models.TextField()