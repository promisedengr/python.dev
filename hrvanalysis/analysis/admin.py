from django.contrib import admin
from .models import Subject, Sample, Result

admin.site.register([Subject, Sample, Result])
