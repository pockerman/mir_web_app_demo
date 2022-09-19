import json
import requests
from pathlib import Path
from django.shortcuts import redirect
from django.http import HttpResponse
from django.template import loader

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login

from mir_web_app_demo.settings import MEDIA_URL
from mir_app.utils import count_number_of_files
from mir_app.forms import SurveyorLogin
from mir_app.template_views import template_ids
# configuration
from mir_app.config import MIR_APP_REST_API
from mir_app.config import SURVEYS_PATH
from mir_app.config import TOTAL_IMAGE_COUNTER


class SurveyorViewHandler(object):

    @staticmethod
    def surveyor_profile(request, surveyor_id: str, template):

        # find the owner via email
        url = MIR_APP_REST_API + f'surveyors/{surveyor_id}'

        response = requests.get(url=url)
        response_json = response.json()

        #  from the surveys list query
        # those that are either pending
        # or in progress
        surveys_ids = response_json['surveys']

        in_progress_surveys = []
        pending_surveys = []

        for survey_id in surveys_ids:

            survey_url = MIR_APP_REST_API + f'surveys/{survey_id}'
            survey_response = requests.get(url=survey_url)
            survey_response = survey_response.json()

            survey_result_url = MIR_APP_REST_API + f'surveys/{survey_id}/survey-result'
            survey_result_response = requests.get(url=survey_result_url)
            survey_result_response = survey_result_response.json()

            vessel_url = MIR_APP_REST_API + f'vessels/{survey_response["vessel_idx"]}/?mmsi=true&ce=true'
            vessel_response = requests.get(url=vessel_url)
            vessel_response = vessel_response.json()

            if survey_result_response['owner_survey_status'] == 'COMPLETED' and \
                survey_result_response['survey_request_status'] == 'PENDING':

                pending_surveys.append((vessel_response['name'],
                                        survey_response['survey_type'],
                                        survey_response['created_at'].split(" ")[0],
                                        survey_response['idx'],
                                        survey_result_response['survey_request_status']))

            elif survey_result_response['owner_survey_status'] == 'COMPLETED' and \
                survey_result_response['survey_request_status'] == 'IN_PROGRESS':

                in_progress_surveys.append((vessel_response['name'],
                                            survey_response['survey_type'],
                                            survey_response['created_at'].split(" ")[0],
                                            survey_response['idx'],
                                            survey_result_response['survey_request_status']))

        surveys = in_progress_surveys + pending_surveys

        context = {'user_auth': True,
                   'user_surveyor_auth': True, 'surveyor_name': response_json['name'],
                   'surveyor_id': surveyor_id,
                   'survey_reqs': surveys}

        return HttpResponse(template.render(context, request))

    @staticmethod
    def login_surveyor(request, template):

        if request.method == 'POST':
            form = SurveyorLogin(request.POST)

            if form.is_valid():
                surveyor_email = form.cleaned_data['surveyor_email']
                surveyor_password = form.cleaned_data['surveyor_password']

                url = MIR_APP_REST_API + f'surveyors/login'
                data = {'email': surveyor_email, 'password': surveyor_password}
                response = requests.post(url=url, data=json.dumps(data))

                response_json = response.json()
                surveyor_id = response_json['idx']

                if not User.objects.filter(username=surveyor_email).exists():
                    print("User in none")
                    context = {"error_email": "The email does not exist"}
                    return HttpResponse(template.render(context, request))

                user = authenticate(request, username=surveyor_email, password=surveyor_password)

                if user is not None:

                    # attempt to login the user
                    login(request=request, user=user)
                    post_next = request.POST.get('next')

                    if post_next is not None:
                        redirect(to=post_next)

                    return redirect(to=f'/surveyor/{surveyor_id}/dashboard/')
                else:
                    print("User in none")
                    context = {"error_email": "Email is invalid"}
                    return HttpResponse(template.render(context, request))
            else:
                context = {"error_email": "Invalid form"}
                return HttpResponse(template.render(context, request))

        context = {}
        return HttpResponse(template.render(context, request))

    @staticmethod
    def surveyor_settings_view(request, surveyor_id: str, template):
        context = {'user_auth': True,
                   'user_surveyor_auth': True,
                   'surveyor_id': surveyor_id}
        return HttpResponse(template.render(context, request))

    @staticmethod
    def surveyor_survey_view(request, surveyor_id: str, survey_id: str, template):

        # get the survey results
        survey_url = MIR_APP_REST_API + f'surveys/{survey_id}'
        survey_response = requests.get(url=survey_url)
        survey_response = survey_response.json()

        survey_name = survey_response['survey_type']
        request_date = survey_response['created_at'].split(" ")[0]

        survey_result_url = MIR_APP_REST_API + f'surveys/{survey_id}/survey-result'
        survey_result_response = requests.get(url=survey_result_url)
        survey_result_response = survey_result_response.json()

        survey_request_state = survey_result_response['survey_request_status']

        context = {'user_auth': True,
                   'user_surveyor_auth': True,
                   'survey_name': survey_name,
                   'request_date': request_date,
                   'survey_request_state': survey_request_state,
                   'surveyor_id': surveyor_id,
                   'survey_id': survey_id,
                   'n_total_photos': 15}

        return HttpResponse(template.render(context, request))

    @staticmethod
    def surveyor_start_survey_view(request, surveyor_id: str, survey_id: str, template):

        def get_survey_items_wrappers_response(survey_id):

            # get the survey item wrappers
            url = MIR_APP_REST_API + f'surveys/{survey_id}/items-wrappers'
            survey_items_wrappers_response = requests.get(url=url)
            survey_items_wrappers_response = survey_items_wrappers_response.json()
            vessel_parts = []

            for item_wrapper in survey_items_wrappers_response:
                wrapper_type = item_wrapper['type']
                wrapper_idx = item_wrapper['idx']
                surveyed_by_owner = item_wrapper['surveyed_by_surveyor']
                vessel_parts.append((wrapper_idx, wrapper_type, surveyed_by_owner))
            return vessel_parts

        vessel_parts = get_survey_items_wrappers_response(survey_id=survey_id)

        # set the survey status to start
        url = MIR_APP_REST_API + f'surveys/{survey_id}/start-survey'
        survey_items_wrappers_response = requests.patch(url=url)
        survey_items_wrappers_response = survey_items_wrappers_response.json()

        context = {'user_auth': True,
                   'user_surveyor_auth': True,
                   'surveyor_id': surveyor_id,
                   'vessel_parts': vessel_parts,
                   'survey_id': survey_id}
        return HttpResponse(template.render(context, request))

    @staticmethod
    def surveyor_vessel_part_subpart_images(request, surveyor_id: str,
                                        survey_id: str, vessel_part_id: str,
                                        vessel_subpart_id: str, template):

        vessel_part_url = MIR_APP_REST_API + f'items-wrappers/{vessel_part_id}'
        vessel_part_response = requests.get(url=vessel_part_url)
        vessel_part_response = vessel_part_response.json()
        vessel_part = vessel_part_response['type']

        vessel_subpart_url = MIR_APP_REST_API + f'items-wrappers/survey-parts/{vessel_subpart_id}'
        vessel_subpart_response = requests.get(url=vessel_subpart_url)
        vessel_subpart_response = vessel_subpart_response.json()
        vessel_subpart = vessel_subpart_response['type']

        # collect the images
        image_path = SURVEYS_PATH / survey_id / vessel_part / vessel_subpart
        tmp_images = count_number_of_files(filepath=image_path, postfix=['jpg', 'png', 'jpeg'])

        images = []
        for img in tmp_images:
            img = str(img)
            img_details = img.split("/")
            img = survey_id + "/" + vessel_part + "/" + vessel_subpart + "/" + img_details[-1]
            img_new = img_details[-1]
            images.append((img, img_new))

        print(images)

        context = {'user_surveyor_auth': True, 'surveyor_id': surveyor_id,
                   'survey_id': survey_id, 'vessel_part': vessel_part,
                   'vessel_subpart': vessel_subpart,
                   'img_counter': len(images), 'vessel_part_id': vessel_part_id,
                   'vessel_subpart_id': vessel_subpart_id,
                   "total_img_counter": TOTAL_IMAGE_COUNTER,
                   'images': images, 'media_url': MEDIA_URL}

        if request.method == 'POST':

            findings = request.POST.get('findings', " ")
            if findings == " ":
                context['error_findings'] = "You need to add your findings"
                return HttpResponse(template.render(context, request))

            recommendations = request.POST.get('recommendations', " ")
            if recommendations == " ":
                context['error_recommendations'] = "You need to add your recommendations"
                return HttpResponse(template.render(context, request))

            # submit the vessel sub part
            # review and findings
            vessel_subpart_url = MIR_APP_REST_API + f'items-wrappers/survey-parts/{vessel_subpart_id}'

            data = {'findings': findings,
                    'recommendations': recommendations,
                    'surveyed_by_surveyor': True}
            vessel_subpart_response = requests.patch(url=vessel_subpart_url, data=json.dumps(data))

            return redirect(to=f'/surveyor/{surveyor_id}/surveys/{survey_id}/vessel_part/{vessel_part_id}/')

        # not a POST simply render the view
        return HttpResponse(template.render(context, request))

    @staticmethod
    def surveyor_survey_part_view(request, surveyor_id: str, survey_id: str, vessel_part_id: str, template):

        def get_item_wrapper_parts(vessel_part_id):
            url = MIR_APP_REST_API + f'items-wrappers/{vessel_part_id}'
            response = requests.get(url=url)
            response = response.json()

            parts = []

            for part in response['survey_parts']:
                url = MIR_APP_REST_API + f'items-wrappers/survey-parts/{part}'
                response_part = requests.get(url=url)
                response_part = response_part.json()
                parts.append((response_part['idx'], response_part['type'],
                              response_part['surveyed_by_surveyor'], len(response_part['images'])))

            return parts, response['type']

        parts, vessel_part = get_item_wrapper_parts(vessel_part_id=vessel_part_id)

        context = {'user_surveyor_auth': True, 'surveyor_id': surveyor_id,
                   'survey_id': survey_id, 'vessel_part_id': vessel_part_id,
                   'vessel_part': vessel_part, 'parts': parts}

        return HttpResponse(template.render(context, request))

    @staticmethod
    def survey_report_write(request, surveyor_id: str, survey_id: str, page: int):

        template = loader.get_template(template_ids['surveyor_survey_write_survey'][page])
        context = {'user_surveyor_auth': True, 'surveyor_id': surveyor_id,
                   'survey_id': survey_id}

        if page == 0:
            # get the hull information
            context["item_wrapper_type"] = "1. Hull shell"
            context["item_wrapper_parts"] = ["1.1	HIN", "1.2	Transom (name)", "1.3	Hull forward SB"]
                                             #"1.4	Hull forward PS", "1.5	Hull midship SB",
                                             #"1.6	Hull midship PS", "1.7	Hull aft SB", "1.8	Hull aft PS",
                                             #"1.9	Transom door/garage"]
        elif page == 1:
            # get the hull information
            context["item_wrapper_type"] = "2. Deck, superstructure & cockpit"
            context["item_wrapper_parts"] = ["2.1 Foredeck", "2.2 Non-skid surfacing", "2.3	Deck aft"]

        return HttpResponse(template.render(context, request))




