from rest_framework import serializers
from django_countries.serializers import CountryFieldMixin
from django.contrib.auth.models import User
from users.models import Profile
import json
import biosppy
from analysis.models import Subject, Result, Sample
from analysis import pyhrv
from analysis.pyhrv import tools as tools
from analysis.utils import fig_to_html

class ProfileSerializer(CountryFieldMixin, serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Profile
		fields = '__all__'

class UserSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = User
		fields = ['id', 'url', 'username', 'email']


class SubjectSerializer(serializers.HyperlinkedModelSerializer):
	user = UserSerializer(read_only=True)
	class Meta:
		model = Subject
		fields = ['id', 'url', 'name', 'gender', 'age', 'user']


class ResultSerializer(serializers.HyperlinkedModelSerializer):
	settings = serializers.DictField(allow_empty=True, allow_null=True)
	radar_chart_params = serializers.DictField(allow_empty=True, allow_null=True)
	parameters = serializers.DictField(allow_empty=True, read_only=True)
	nn_histogram = serializers.ReadOnlyField()
	poincare_plot = serializers.ReadOnlyField()
	lomb_plot = serializers.ReadOnlyField()
	dfa_plot = serializers.ReadOnlyField()
	tachogram_plot = serializers.ReadOnlyField()
	fft_plot = serializers.ReadOnlyField()
	radar_plot = serializers.ReadOnlyField()
	class Meta:
		model = Result
		fields = '__all__'



class SampleSerializer(serializers.HyperlinkedModelSerializer):
	data = serializers.ListField(child=serializers.FloatField())
	
	class Meta:
		model = Sample
		fields = ['id', 'url' , 'subject', 'comment', 'data']