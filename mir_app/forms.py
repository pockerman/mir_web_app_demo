from django.forms import ModelForm
from django import forms


class OwnerLogin(forms.Form):
    owner_password = forms.CharField(required=True, max_length=50)
    owner_email = forms.EmailField(required=True)


class OnwerSignUpForm(forms.Form):
    owner_password = forms.CharField(required=False, max_length=50)
    owner_password_confirm = forms.CharField(required=False, max_length=50)
    owner_email = forms.EmailField(required=False)
    owner_name = forms.CharField(required=False, max_length=50)
    owner_surname = forms.EmailField(required=False,  max_length=50)


class SurveyorLogin(forms.Form):
    surveyor_password = forms.CharField(required=True, max_length=50)
    surveyor_email = forms.EmailField(required=True)


class VesselRegistration(forms.Form):
    vessel_name = forms.CharField(required=False, max_length=50)
    vessel_id = forms.CharField(required=False, max_length=50)
    mmsi_id = forms.CharField(required=False, max_length=50)
    ce_id = forms.CharField(required=False, max_length=50)
    vessel_type = forms.CharField(required=True, max_length=50)
    construction_material_type = forms.CharField(required=True, max_length=50)


class GenerateSurveyForm(forms.Form):
    survey_type = forms.CharField(required=True, max_length=50)


class UploadImgForm(forms.Form):
    image = forms.ImageField(required=True)
    image_tags = forms.CharField(required=False, max_length=100)
