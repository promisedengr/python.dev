from django.db import models
from django.contrib.auth.models import User
import biosppy
from analysis import pyhrv
from analysis.pyhrv import tools as tools
from analysis.utils import fig_to_html

class Subject(models.Model):
	GENDER = [
		("male", "M" ),
		("female", "F" )
	]
	name = models.CharField(max_length=150, default='John Doe', blank=True)
	gender = models.CharField(max_length=20, choices=GENDER, default="male", blank=True)
	age = models.PositiveIntegerField(default=18, blank=True)
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subjects')
	date_created = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['name']	

	def __str__(self):
		return self.name

class Sample(models.Model):
	subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='samples')
	comment = models.TextField(blank=True)
	last_modified = models.DateTimeField(auto_now=True)	        
	data = models.JSONField(null=True)

	class Meta:
		ordering = ['-last_modified']

	def __str__(self):
		return f'Sample {self.pk}'



class Result(models.Model):
	sample = models.OneToOneField(Sample, on_delete=models.CASCADE, primary_key=True, related_name='result')
	settings = models.JSONField(null=True)
	radar_chart_params = models.JSONField(null=True)
	parameters = models.JSONField(null=True)
	nn_histogram = models.TextField(blank=True, help_text='html representation of the nn histogram plot')
	poincare_plot = models.TextField(blank=True, help_text='html representation of the poincare plot')
	lomb_plot = models.TextField(blank=True, help_text='html representation of the lomb plot')
	dfa_plot = models.TextField(blank=True, help_text='html representation of dfa plot')
	tachogram_plot = models.TextField(blank=True, help_text='html representation of tachogram plot')
	fft_plot = models.TextField(blank=True, help_text='html representation of the fft plot')
	radar_plot = models.TextField(blank=True, help_text='html radar plot representation of comparison between two samples')

	def save(self, *args, **kwargs):
		# run this for updates
		if self.parameters:
			settings = {}
			if self.settings:
				settings = {
					'kwargs_time': self.settings.get('kwargs_time', None),
					'interval': self.settings.get('interval', None),
					'fbands': self.settings.get('fbands', None),
					'kwargs_tachogram': self.settings.get('kwargs_tachogram', None),
					'kwargs_nonlinear': self.settings.get('kwargs_nonlinear', None),
					'kwargs_welch': self.settings.get('kwargs_welch', None),
					'kwargs_lomb': self.settings.get('kwargs_lomb', None),					
				}
			
			results = pyhrv.hrv( 
				nni = self.sample.data,
				kwargs_time = settings.get('kwargs_time', None),
				interval = settings.get('interval', None),
				fbands = settings.get('fbands', None),
				kwargs_tachogram = settings.get('kwargs_tachogram', None),
				kwargs_nonlinear = settings.get('kwargs_nonlinear', None),
				kwargs_welch = settings.get('kwargs_welch', None),
				kwargs_lomb = settings.get('kwargs_lomb', None),
				)
				
			self.parameters = {}
			for key in results.keys():
				if isinstance(results[key], biosppy.utils.ReturnTuple):
					self.parameters[key] = dict(results[key])
				elif isinstance(results[key], tuple):
					self.parameters[key] = list(results[key])
				elif isinstance(results[key], str):
					self.parameters[key] = results[key]
				elif isinstance(results[key], range):
					self.parameters[key] = list(results[key])
				elif results[key] is None:
					self.parameters[key] = 'n/a'
				elif 'plot' not in str(key) and 'histogram' not in str(key):
					self.parameters[key] = float(results[key]) if str(results[key]) != 'nan' else 'n/a'

			self.nn_histogram = fig_to_html(results['nni_histogram'])
			self.poincare_plot = fig_to_html(results['poincare_plot'])
			self.lomb_plot = fig_to_html(results['lomb_plot'])
			self.dfa_plot = fig_to_html(results['dfa_plot'])
			self.tachogram_plot = fig_to_html(results['tachogram_plot'])
			self.fft_plot = fig_to_html(results['fft_plot'])

			
			if self.radar_chart_params:
				try:
					# radar plot
					sample_to_compare = Sample.objects.get(pk=self.radar_chart_params['sample_id'])
					
					# Specify the HRV parameters to be computed
					params = self.radar_chart_params.get('parameters',['nni_mean', 'sdnn', 'rmssd', 'sdsd', 'nn50', 'nn20', 'sd1', 'fft_peak'])
					reference_nni = self.sample.data
					comparison_nni = sample_to_compare.data

					comparison_result = tools.radar_chart(nni=reference_nni, comparison_nni=comparison_nni, parameters=params, show=False)			
					self.radar_plot = fig_to_html(comparison_result['radar_plot'])
				except Exception as e:
					print(e.__doc__)
					print(e.message)
		super(Result, self).save(*args, **kwargs)
	def __str__(self):
		return f'Results for sample {self.sample.pk}'