import requests
import json


from mir_app.forms import VesselRegistration
from mir_app.forms import GenerateSurveyForm
from mir_app.forms import UploadImgForm
from mir_app.forms import OnwerSignUpForm

from mir_app.config import MIR_APP_REST_API


def handle_vessel_registration(request, owner_id):

    form = VesselRegistration(request.POST)

    if form.is_valid():
        # if the form is valid make a POST
        # and return the response
        form_data = form.cleaned_data
        print(form_data)

        #vessel_type_url = MIR_APP_REST_API + f'vessels/types/{form_data["vessel_type"]}'
        #vessel_type_response = requests.get(url=vessel_type_url)
        #vessel_type_response = vessel_type_response.json()

        data = {"owner_idx": owner_id,
                "name": form_data['vessel_name'],
                "vessel_type": form_data['vessel_type'],
                'mmsi': form_data['mmsi_id'],
                'ce': form_data['ce_id'],
                "propulsion_type": "motor",
                "operation_years": 10,
                "service_years": 5,
                "loa": 9.23,
                "beam": 10.4,
                "ssr": "123",
                "max_persons": 5,
                "max_passengers": 3,
                "sea_category": False,
                "builder": {
                    "yard": "London Docks Ltd",
                    "location": "London",
                    "maker": "BMW",
                    "year_built": "14/06/1979"
                },
                "hull": {
                  "idx": "l102",
                  "construction_type": form_data['construction_material_type']
               },
        }

        data = json.dumps(data)

        url = MIR_APP_REST_API + 'vessels/'
        request = requests.post(url=url, data=data)
        return request
    else:
        raise ValueError("VesselRegistration is invalid")


def handle_generate_survey(request, owner_id, vessel_id):

    form = GenerateSurveyForm(request.POST)

    if form.is_valid():
        return form.cleaned_data
    else:
        raise ValueError("GenerateSurveyForm is invalid")


def handle_uploaded_img(request, survey_id: str, owner_id: str, vessel_id: str, vessel_part: str, vessel_subpart: str):

    form = UploadImgForm(request.POST, request.FILES)

    if form.is_valid():
        return form.cleaned_data
    else:
        print(form.errors)
        print(form.as_ul())
        raise ValueError("UploadImgForm is invalid")


def handle_owner_signup(request):

    if request.POST.get('owner_name', None) is not None and \
            request.POST.get('owner_surname', None) is not None and \
            request.POST.get('owner_password', None) is not None and \
            request.POST.get('owner_email', None) is not None and \
            request.POST.get('owner_password_confirm', None) is not None:

        return {'owner_name': request.POST.get('owner_name'),
                'owner_surname': request.POST.get('owner_surname'),
                'owner_password': request.POST.get('owner_password'),
                'owner_email': request.POST.get('owner_email'),
                'owner_password_confirm': request.POST.get('owner_password_confirm')}
    else:
        #print(form.errors)
        #print(form.as_ul())
        raise ValueError("OnwerSignUpForm is invalid")


def handle_surveyor_signup(request):

    if request.POST.get('surveyor_name', None) is not None and \
            request.POST.get('surveyor_surname', None) is not None and \
            request.POST.get('surveyor_password', None) is not None and \
            request.POST.get('surveyor_email', None) is not None:

        return {'surveyor_name': request.POST.get('surveyor_name'),
                'surveyor_surname': request.POST.get('surveyor_surname'),
                'surveyor_password': request.POST.get('surveyor_password'),
                'surveyor_email': request.POST.get('surveyor_email')}
    else:
        raise ValueError("SurveyorSignUpForm is invalid")

