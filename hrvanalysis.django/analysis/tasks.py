from celery import shared_task
from .models import Sample, Result
import biosppy
from analysis import pyhrv
from analysis.pyhrv import tools as tools
from analysis.utils import fig_to_html
from django.template.loader import render_to_string
from celery.exceptions import SoftTimeLimitExceeded


@shared_task(bind=True)
def compute_result(self, sample_pk):
	sample = Sample.objects.get(pk=sample_pk)
	
	try:		
		result = Result(sample=sample)

		settings = {}
		if result.settings:
			settings = {
				'kwargs_time': result.settings.get('kwargs_time', None),
				'interval': result.settings.get('interval', None),
				'fbands': result.settings.get('fbands', None),
				'kwargs_tachogram': result.settings.get('kwargs_tachogram', None),
				'kwargs_nonlinear': result.settings.get('kwargs_nonlinear', None),
				'kwargs_welch': result.settings.get('kwargs_welch', None),
				'kwargs_lomb': result.settings.get('kwargs_lomb', None),					
			}
		
		results = pyhrv.hrv( 
			nni = result.sample.data,
			kwargs_time = settings.get('kwargs_time', None),
			interval = settings.get('interval', None),
			fbands = settings.get('fbands', None),
			kwargs_tachogram = settings.get('kwargs_tachogram', None),
			kwargs_nonlinear = settings.get('kwargs_nonlinear', None),
			kwargs_welch = settings.get('kwargs_welch', None),
			kwargs_lomb = settings.get('kwargs_lomb', None),
			)
			
		result.parameters = {}
		for key in results.keys():
			if isinstance(results[key], biosppy.utils.ReturnTuple):
				result.parameters[key] = dict(results[key])
			elif isinstance(results[key], tuple):
				result.parameters[key] = list(results[key])
			elif isinstance(results[key], str):
				result.parameters[key] = results[key]
			elif isinstance(results[key], range):
				result.parameters[key] = list(results[key])
			elif results[key] is None:
				result.parameters[key] = 'n/a'
			elif 'plot' not in str(key) and 'histogram' not in str(key):
				result.parameters[key] = float(results[key]) if str(results[key]) != 'nan' else 'n/a'

		result.nn_histogram = fig_to_html(results['nni_histogram'])
		result.poincare_plot = fig_to_html(results['poincare_plot'])
		result.lomb_plot = fig_to_html(results['lomb_plot'])
		result.dfa_plot = fig_to_html(results['dfa_plot'])
		result.tachogram_plot = fig_to_html(results['tachogram_plot'])
		result.fft_plot = fig_to_html(results['fft_plot'])

		
		if result.radar_chart_params:
			try:
				# radar plot
				sample_to_compare = Sample.objects.get(pk=result.radar_chart_params['sample_id'])
				
				# Specify the HRV parameters to be computed
				params = result.radar_chart_params.get('parameters',['nni_mean', 'sdnn', 'rmssd', 'sdsd', 'nn50', 'nn20', 'sd1', 'fft_peak'])
				reference_nni = result.sample.data
				comparison_nni = sample_to_compare.data

				comparison_result = tools.radar_chart(nni=reference_nni, comparison_nni=comparison_nni, parameters=params, show=False)			
				result.radar_plot = fig_to_html(comparison_result['radar_plot'])
			except:
				pass
		
		result.save()

		return "Done"
	except SoftTimeLimitExceeded:		
		user = sample.subject.user
		subject = 'Time limit exceeded'
		message = render_to_string('analysis/result-failed-email.html', {
			'user': user,
			'comment': sample.comment
		})
		user.email_user(subject, message)

		sample.delete()
		return "Failed"