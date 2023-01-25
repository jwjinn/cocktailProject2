from django.db import models

class board(models.Model):
    title = models.TextField()
    contents = models.TextField()
    image = models.ImageField(upload_to= 'images/', null = True, blank=True)

