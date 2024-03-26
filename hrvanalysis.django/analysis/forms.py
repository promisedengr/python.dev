from django import forms
from .models import Sample
from django.core.exceptions import ValidationError

class ResultSettingsForm(forms.Form):
	threshold = forms.IntegerField(required=False, label='Threshold', help_text='Custom threshold in [ms] for the optional NNXX and pNNXX parameters')
	binsize = forms.FloatField(required=False, label='Bins', help_text='Bin size in [ms] of the histogram bins')
	tachogram_title = forms.CharField(required=False, max_length=200)
	tachogram_hr = forms.BooleanField(required=False, label='Show heart rate')
	interval_lower = forms.IntegerField(required=False, label='', help_text='Lower bound of the visualization interval of the Tachogram plot')
	interval_upper = forms.IntegerField(required=False, label='', help_text='Upper bound of the visualization interval of the Tachogram plot')

	def clean(self):
		super().clean()
		interval_lower = self.cleaned_data.get('interval_lower')
		interval_upper = self.cleaned_data.get('interval_upper')
		if interval_lower > interval_upper: self._errors['interval_lower'] = self.error_class(['Must be less than the upper bound'])
		if interval_upper < 0 : self._errors['interval_upper'] = self.error_class(['Upper bound is greater than 0'])
		if interval_lower < 0 : self._errors['interval_lower'] = self.error_class(['Lower bound is greater than 0'])
		return self.cleaned_data
