from django import forms

class PatientCheckinForm(forms.Form):
    first_name = forms.CharField(label='First name', required=True )
    last_name = forms.CharField(label='Last name', required = True)
    social_security_number = forms.DecimalField(label = 'Social security number', max_digits = 9, required = False)

class PatientDemographicsForm(forms.Form):
    id = forms.IntegerField(widget = forms.HiddenInput)
    address = forms.CharField(label = 'Address', required = False)
    cell_phone = forms.IntegerField(label = 'Cell number', required = False)
    email = forms.EmailField(label= 'Email', required = False)
    zip_code = forms.IntegerField(label = 'Zip code', required =  False)
