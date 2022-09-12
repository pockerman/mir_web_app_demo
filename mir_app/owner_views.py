import json
import requests
from django.shortcuts import redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login

from mir_app.forms import OwnerLogin
from mir_app.models import Owner

MIR_APP_REST_API = 'http://127.0.0.1:8000/api/v1/'

PASS_CHARACTERS = ['_', "#", "!", ]


def valid_characters(string, characters):
    for c in string:
        if c in characters:
            return True
    return False


class OwnerViewsHandler(object):

    @staticmethod
    def owner_profile(request, owner_id: str, template):
        """Renders the owner profile

          Parameters
          ----------
          request

          Returns
          -------
        """

        # find the owner via email
        url = MIR_APP_REST_API + f'owners/{owner_id}'

        response = requests.get(url=url)
        response_json = response.json()

        context = {'user_auth': True, 'owner_name': response_json['name'],
                   'owner_id': response_json['idx']}

        vessels = []

        for vessel in response_json['vessels']:
            if vessel != "":
                # do the query and get the vessel data
                # name and mmsi
                url = MIR_APP_REST_API + f'vessels/{vessel}/?mmsi=true&ce=true'
                response = requests.get(url=url)
                response_json = response.json()
                vessels.append((vessel, response_json['name'], response_json['mmsi'], response_json['ce']))

        if len(vessels) != 0:
            context['vessels'] = vessels

        return HttpResponse(template.render(context, request))


    @staticmethod
    def sign_up(request, form_data, template):

        # check if the owner exists
        url = MIR_APP_REST_API + 'owners/get'

        owner_email = form_data['owner_email']
        owner_password = form_data['owner_password']
        name = form_data['owner_name']
        surname = form_data['owner_surname']
        data = {'email': owner_email}

        response = requests.post(url=url, data=json.dumps(data))
        response = response.json()

        if 'email' in response:
            context = {"error_email": "Email exists"}
            return HttpResponse(template.render(context, request))
        elif len(name) < 2:
            context = {"error_name": "A name should have at least two letters."}
            return HttpResponse(template.render(context, request))
        elif len(surname) < 2:
            context = {"error_surname": "A surname should have at least two letters."}
            return HttpResponse(template.render(context, request))
        elif not valid_characters(owner_password, PASS_CHARACTERS):
            context = {"password_not_valid_characters": "Invalid password."}
            return HttpResponse(template.render(context, request))
        elif owner_password != form_data['owner_password_confirm']:
            context = {"confirm_password_error": "Passwords do not match."}
            return HttpResponse(template.render(context, request))
        else:

            # send the data to the DB
            url = MIR_APP_REST_API + 'owners/signup'

            owner_password = form_data['owner_password']
            name = form_data['owner_name']
            surname = form_data['owner_surname']

            post_data = json.dumps({'name': name, 'surname': surname,
                                    'email': owner_email, 'password': owner_password})

            # we need to add the data to the model too
            owner = Owner()
            owner.name = name
            owner.surname = surname
            owner.password = owner_password
            owner.email = owner_email
            owner.save()

            user = User.objects.create_user(username=owner_email, password=owner_password,
                                            email=owner_email,
                                            first_name=name, last_name=surname)
            user.save()

            response = requests.post(url=url, data=post_data)
            response = response.json()

            idx = response['idx']
            return redirect(to=f'/owner/{idx}/verify-email/')

    @staticmethod
    def verify_owner_email(request, owner_id, template):

        if request.method == 'POST':

            url = MIR_APP_REST_API + f'owners/signup/{owner_id}/confirm'
            post_data = json.dumps({'verification_code': str(request.POST.get('code'))})

            requests.post(url=url, data=post_data)
            return redirect('/login/')
        else:

            context = {'owner_id': owner_id}
            return HttpResponse(template.render(context, request))

    @staticmethod
    def login_owner(request, template):

        if request.method == 'POST':
            form = OwnerLogin(request.POST)

            if form.is_valid():
                owner_email = form.cleaned_data['owner_email']
                owner_password = form.cleaned_data['owner_password']

                # login the owner via email and pass
                # find the owner via email
                url = MIR_APP_REST_API + f'owners/login'
                data = {'email': owner_email, 'password': owner_password}
                response = requests.post(url=url, data=json.dumps(data))
                response = response.json()

                if 'has_confirmed_email' in response and response['has_confirmed_email'] is False:
                    context = {"error_email": "Email is invalid"}
                    return HttpResponse(template.render(context, request))

                if 'email' in response:
                    owner_id = response['idx']

                    # TODO: we need to check pass also
                    owner_email = request.POST['owner_email']
                    owner_password = request.POST['owner_password']

                    if not User.objects.filter(username=owner_email).exists():
                        print("User in none")
                        context = {"error_email": "The email does not exist"}
                        return HttpResponse(template.render(context, request))

                    user = authenticate(request, username=owner_email, password=owner_password)

                    if user is not None:

                        # attempt to login the user
                        login(request=request, user=user)
                        post_next = request.POST.get('next')

                        if post_next is not None:
                            redirect(to=post_next)

                        return redirect(to=f'/owner/{owner_id}/dashboard/')
                    else:
                        print("User in none")
                        context = {"error_email": "Email is invalid"}
                        return HttpResponse(template.render(context, request))
                else:
                    context = {"error_email": "Email is invalid"}
                    return HttpResponse(template.render(context, request))

        context = {}
        return HttpResponse(template.render(context, request))

    @staticmethod
    def forget_password(request, template):

        if request.method == 'POST':

            # check the email
            email = request.POST.get('email', None)

            if email is None:
                context = {"error_email": "Email is invalid"}
                return HttpResponse(template.render(context, request))

            # check if email exists
            # check if the owner exists
            url = MIR_APP_REST_API + 'owners/get'

            data = {'email': email}
            response = requests.post(url=url, data=json.dumps(data))
            response = response.json()

            if 'email' not in response:
                context = {"error_email": "Email is invalid"}
                return HttpResponse(template.render(context, request))

            return redirect(to='success-password-reset-email')
        else:
            context = {}
            return HttpResponse(template.render(context, request))

    @staticmethod
    def view_owner_survey_requests(request, owner_id: str, template):

        context = {'user_auth': True, 'owner_id': owner_id}

        # find the owner via email
        url = MIR_APP_REST_API + f'owners/{owner_id}'

        response = requests.get(url=url)
        response_json = response.json()

        # surveys
        in_progress_surveys = []
        pending_surveys_req = []
        in_progress_surveys_req = []
        completed_surveys_reqs = []
        for survey in response_json['surveys']:

            url = MIR_APP_REST_API + f'surveys/{survey}/'
            response = requests.get(url=url)
            survey_response_json = response.json()

            print(survey_response_json)

            if 'status_code' in survey_response_json and \
                    survey_response_json['status_code'] == 404:
                continue

            survey_type = survey_response_json['survey_type']

            # get the vessel name that corresponds to this
            # survey
            vessel_id = survey_response_json['vessel_idx']

            context['vessel_id'] = vessel_id

            url = MIR_APP_REST_API + f'vessels/{vessel_id}/'

            response = requests.get(url=url)
            vessel_response_json = response.json()

            survey_result_doc = MIR_APP_REST_API + f'surveys/{survey}/survey-result'

            survey_result_doc = requests.get(url=survey_result_doc)
            survey_result_response_json = survey_result_doc.json()

            print(survey_response_json)

            if survey_result_response_json['owner_survey_status'] == "IN_PROGRESS":
                in_progress_surveys.append((survey, vessel_response_json['name'],
                                            survey_type,
                                            survey_response_json['created_at'].split(" ")[0],
                                            "IN PROGRESS"))
            elif survey_result_response_json['survey_request_status'] == "PENDING":
                pending_surveys_req.append((survey, vessel_response_json['name'],
                                            survey_type,
                                            survey_response_json['created_at'].split(" ")[0],
                                            'PENDING'))
            elif survey_result_response_json['survey_request_status'] == "IN_PROGRESS":
                in_progress_surveys_req.append((survey, vessel_response_json['name'],
                                                survey_type,
                                                survey_response_json['created_at'].split(" ")[0],
                                                "IN_PROGRESS"))
            elif survey_result_response_json['survey_request_status'] == "COMPLETED":
                completed_surveys_reqs.append((survey, vessel_response_json['name'],
                                               survey_type,
                                               survey_response_json['created_at'].split(" ")[0],
                                               "COMPLETED"))

        context['in_progress_surveys'] = in_progress_surveys
        context['pending_surveys_reqs'] = pending_surveys_req
        context['in_progress_surveys_reqs'] = in_progress_surveys_req
        context['completed_surveys_reqs'] = completed_surveys_reqs

        return HttpResponse(template.render(context, request))

    @staticmethod
    def subscription_view(request, owner_id: str, template):

        url = MIR_APP_REST_API + f'owners/{owner_id}'
        response = requests.get(url=url)
        response = response.json()

        context = {'user_auth': True,
                   'owner_id': owner_id,
                   'subscription_type': response['subscription_plan_id']}
        return HttpResponse(template.render(context, request))

    @staticmethod
    def delete_owner(request, owner_id) -> HttpResponse:
        """Handles the delete view

        Parameters
        ----------
        request
        owner_id: The id of the owner to delete

        Returns
        -------
        An instance of HttpResponse
        """

        # find the owner via email
        url = MIR_APP_REST_API + f'owners/{owner_id}'
        response = requests.delete(url=url)
        return redirect(to='/login/')

