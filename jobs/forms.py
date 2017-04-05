from django import forms
from datetime import date
import warnings
from mails.models import *
from .models import * 
from django.core import validators


# class add_keyword(forms.ModelForm):
# 	class Meta:
# 		model=keyword_search
# 		fields=('keyword_name','discription',)

# 	def clean_key(self):
# 		print(self.cleaned_data)
# 		keyword_name      = self.cleaned_data.get('keyword_name')
# 		print(keyword_name)

# 		keyword_qs = keyword_search.objects.filter(Keyword_name=keyword_name)
# 		if  keyword_qs.exists():
# 			raise forms.ValidationError("This keyword has  already been registered")
# 		else:
# 			return keyword_name

	
