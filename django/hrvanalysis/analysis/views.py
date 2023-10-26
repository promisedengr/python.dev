from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import os
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib.staticfiles import finders

from .models import Subject, Sample, Result
from .forms import ResultSettingsForm
import pandas as pd
import json
import datetime
from opensignalsreader import OpenSignalsReader
from biosppy.signals.ecg import ecg
import analysis.pyhrv.tools as tools
from .utils import fig_to_html


# subject
@login_required
def subject_list(request):
	""" 
	CRUD subjects
	"""
	return render(request, 'analysis/subject-list.html')

@login_required
def subject_sample_list(request, pk):
	""" 
	CRUD samples
	"""
	subject = get_object_or_404(Subject, pk=pk)
	return render(request, 'analysis/subject-sample-list.html',{'subject':subject})

@login_required
def preview_file(request, pk):
	""" 
	preview the uploaded files on the current subject
	"""
	subject = get_object_or_404(Subject, pk=pk)
	def get_ecg_data(ecgfile):
		fpath = ecgfile.temporary_file_path()
		# Load the acquisition file
		acq = OpenSignalsReader(fpath)
		# Get the ECG signal
		signal = acq.signal('ECG')
		# Filter ECG signal and extract the R-peak locations
		filtered_signal, rpeaks = ecg(signal, show=False)[1:3]
		return filtered_signal, rpeaks
		
	nni_data = {}
	data_preview = {}
	if request.method == "POST":
		ecg_files = request.FILES.getlist('ecgFiles')
		nni_files = request.FILES.getlist('nniFiles')
		
		if ecg_files:
			for i, ecg_file in enumerate(ecg_files):
				try:
					filtered_signal, rpeaks = get_ecg_data(ecgfile=ecg_file)					
					# Compute NNI parameters
					nni = tools.nn_intervals(rpeaks)
					nni_data[f'{ecg_file.name}_{i}'] = nni.tolist()
					# ECG plot
					fig = tools.plot_ecg(signal=filtered_signal, show=False)['ecg_plot']
					data_preview[f'{ecg_file.name}_{i}'] = fig_to_html(fig)
				except Exception as e:
					messages.info(request, f'Something went wrong while trying to read the file(s)')
					print(e.__doc__)
					print(e.message)
					return redirect('subject_sample_list', pk=subject.pk)
		elif nni_files:
			for i, nni_file in enumerate(nni_files):
				try:
					df = pd.read_csv(nni_file)
					data_preview[f'{nni_file.name}_{i}'] = df.head().to_html(classes='table table-striped dataFile')
					for columnName, columnData in df.iteritems():
						nni_data[f'{nni_file.name}_{i}_{columnName}'] = columnData.dropna().tolist()			
					
				except Exception as e:
					messages.info(request, f'Something went wrong while trying to read the file(s)')
					print(e.__doc__)
					print(e.message)
					return redirect('subject_sample_list', pk=subject.pk)
	context = {
		'data_preview' : data_preview,
		'nni_data' : json.dumps(nni_data),
		'subject': subject,
	}
	return render(request, 'analysis/preview.html', context)

@login_required
def analysis_board(request, pk):
	""" 
	Update result , sample comment and display
	analysis results 
	"""
	result = get_object_or_404(Result, pk=pk)
	form = ResultSettingsForm()
	try:
		# pnnxx and nnxx
		ct = result.settings['kwargs_time']['threshold']
		custom_threshold = (f'pnn{ct}', result.parameters[f'pnn{ct}'], f'nn{ct}', result.parameters[f'nn{ct}'])
	except:
		custom_threshold = ("ppxx", "n/a", "nnxx", "n/a")
	context = {
		'form':form,
		'result':result,
		'custom_threshold':custom_threshold,
	}
	return render(request, 'analysis/analysis-board.html', context)



def link_callback(uri, rel):
	"""
	Convert HTML URIs to absolute system paths so xhtml2pdf can access those
	resources
	"""
	result = finders.find(uri)
	if result:
		if not isinstance(result, (list, tuple)):
				result = [result]
		result = list(os.path.realpath(path) for path in result)
		path=result[0]
	else:
		sUrl = settings.STATIC_URL        # Typically /static/
		sRoot = settings.STATIC_ROOT      # Typically /home/userX/project_static/
		mUrl = settings.MEDIA_URL         # Typically /media/
		mRoot = settings.MEDIA_ROOT       # Typically /home/userX/project_static/media/

		if uri.startswith(mUrl):
			path = os.path.join(mRoot, uri.replace(mUrl, ""))
		elif uri.startswith(sUrl):
			path = os.path.join(sRoot, uri.replace(sUrl, ""))
		else:
			return uri

	# make sure that file exists
	if not os.path.isfile(path):
		raise Exception(
			'media URI must start with %s or %s' % (sUrl, mUrl)
		)
	return path

@login_required
def result_render_pdf(request, pk):
	""" 
	generates pdf reports
	"""
	template_path = 'analysis/pdf-report.html'
	result = get_object_or_404(Result, pk=pk)
	try:
		# pnnxx and nnxx
		ct = result.settings['kwargs_time']['threshold']
		custom_threshold = (f'pnn{ct}', result.parameters[f'pnn{ct}'],f'nn{ct}', result.parameters[f'nn{ct}'])
	except:
		custom_threshold = ("ppxx", "-", "nnxx", "-")
	context = {'result': result, 'custom_threshold' : custom_threshold}
	# Create a Django response object, and specify content_type as pdf
	now=datetime.datetime.now()
	para = f'attachment; filename="HRVSciHub_report_{now.strftime("%Y-%m-%d %H:%M:%S")}.pdf"'
	response = HttpResponse(content_type='application/pdf')
	response['Content-Disposition'] = para
	# find the template and render it.
	template = get_template(template_path)
	html = template.render(context)

	# create a pdf
	pisa_status = pisa.CreatePDF(
	   html, dest=response, link_callback=link_callback)
	# if error then show some funy view
	if pisa_status.err:
	   return HttpResponse('We had some errors <pre>' + html + '</pre>')
	return response


def error_404(request, *args, **kwargs):
        return render(request,'analysis/404.html',{})

def error_500(request, *args, **kwargs):
        return render(request,'analysis/500.html',{})
        
def error_403(request, *args, **kwargs):
        return render(request,'analysis/403.html',{})

def error_400(request, *args, **kwargs):
        return render(request,'analysis/400.html',{}) 