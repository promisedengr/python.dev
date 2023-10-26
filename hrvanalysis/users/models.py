from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField

class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
	image = models.ImageField(upload_to='avatars', blank=True)
	first_name = models.CharField(default='', blank=True, max_length=100)
	last_name = models.CharField(default='', blank=True, max_length=100)
	city = models.CharField(default='', blank=True, max_length=100)
	address = models.CharField(default='', blank=True, max_length=200)
	address2 = models.CharField(default='', blank=True, max_length=200)
	country = CountryField(blank_label='(select country)', blank=True, default='')
	email_confirmed = models.BooleanField(default=False)

	def __str__(self):
		return f'{self.user.username} Profile'