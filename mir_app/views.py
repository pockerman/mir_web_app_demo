import mimetypes
import json
from pathlib import Path
import requests


from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.models import User

from mir_web_app_demo.settings import MEDIA_URL

from mir_app.forms import OwnerLogin
from mir_app.forms import SurveyorLogin
from mir_app.utils import count_number_of_files
from mir_app.form_handlers import handle_owner_signup
from mir_app.form_handlers import handle_surveyor_signup

from mir_app.owner_views import OwnerViewsHandler
from mir_app.vessel_views import VesselViewsHandler
from mir_app.survey_views import SurveyViewHandler
from mir_app.subscription_views import SubscriptionsViewHandler
from mir_app.surveyor_views import SurveyorViewHandler
from mir_app.template_views import template_ids

from mir_app.config import MIR_APP_REST_API
from mir_app.config import TOTAL_IMAGE_COUNTER
from mir_app.config import SURVEYS_PATH

#MIR_APP_REST_API = 'http://127.0.0.1:8000/api/v1/'
#SURVEYS_PATH = Path("/home/alex/qi3/mir_app_web_app/surveys")
#OWNER_ID = '6306179d0eb28a571d11c282'
#TOTAL_IMAGE_COUNTER = 5


def keep_user_log_in(request, context):

    if request.user.is_authenticated:

        if request.user.email == 'a.giavaras@gmail.com':
            url = MIR_APP_REST_API + f'surveyors/login'

            # get the user idx
            data = {'email': 'a.giavaras@gmail.com', 'password': '123'}
            response = requests.post(url=url, data=json.dumps(data))

            response_json = response.json()
            surveyor_id = response_json['idx']
            context['user_auth'] = True
            context['user_surveyor_auth'] = True
            context['surveyor_id'] = surveyor_id
            return context
        else:

            url = MIR_APP_REST_API + f'owners/login'

            # get the user idx
            data = {'email': 'alex@navalmartin.com', 'password': '123'}
            response = requests.post(url=url, data=json.dumps(data))

            response_json = response.json()
            surveyor_id = response_json['idx']
            context['user_auth'] = True
            context['owner_id'] = surveyor_id
            return context


def index(request) -> HttpResponse:
    """Renders the index view of the mir-app

      Parameters
      ----------
      request

      Returns
      -------

    """
    template = loader.get_template(template_ids['index'])
    context = {}
    context = keep_user_log_in(request=request, context=context)
    return HttpResponse(template.render(context, request))


def about(request):
    """Renders the about page

      Parameters
      ----------
      request

      Returns
      -------
    """

    template = loader.get_template(template_ids['about'])
    context = {}
    context = keep_user_log_in(request=request, context=context)
    return HttpResponse(template.render(context, request))


def terms_and_conditions(request) -> HttpResponse:
    """Renders the T&Cs of the mir-app

      Parameters
      ----------
      request

      Returns
      -------

    """
    template = loader.get_template(template_ids['terms_and_conditions'])
    context = {}
    context = keep_user_log_in(request=request, context=context)
    return HttpResponse(template.render(context, request))


def pricing(request) -> HttpResponse:
    """Rendenrs the pricing page

      Parameters
      ----------
      request

      Returns
      -------

    """

    template = loader.get_template(template_ids['pricing'])
    context = {'Pro': 'Pro', 'Enterprise': 'Enterprise', 'Free': 'Free'}
    context = keep_user_log_in(request=request, context=context)
    return HttpResponse(template.render(context, request))


def contact(request):
    template = loader.get_template(template_ids['contact'])
    context = {}
    context = keep_user_log_in(request=request, context=context)
    return HttpResponse(template.render(context, request))


def data_privacy_view(request):
    template = loader.get_template(template_ids['data_privacy_view'])
    context = {}
    context = keep_user_log_in(request=request, context=context)
    return HttpResponse(template.render(context, request))


def signup(request):

    template = loader.get_template(template_ids['signup'])
    if request.method == 'POST':

        try:
            form_data = handle_owner_signup(request=request)
        except ValueError:
            form_data = handle_surveyor_signup(request=request)

        if 'owner_name' in form_data:
            # signup the owner
            return OwnerViewsHandler.sign_up(request, form_data, template)

        elif 'surveyor_name' in form_data:
            # send the data to the DB
            url = MIR_APP_REST_API + 'surveyors/signup'

            owner_email = form_data['surveyor_email']
            owner_password = form_data['surveyor_password']
            name = form_data['surveyor_name']
            surname = form_data['surveyor_surname']

            post_data = json.dumps({'name': name, 'surname': surname,
                                    'email': owner_email,
                                    'password': owner_password,
                                    'signature_file': 'signature.png',
                                    'image_encoding': 'latin1'})

            response = requests.post(url=url, data=post_data)
            response = response.json()

            idx = response['idx']
            return redirect(to=f'/surveyor/{idx}/verify-email/')
        else:
            raise ValueError("Invalid role signup")
    else:

        template = loader.get_template(template_ids['signup'])
        context = {}
        return HttpResponse(template.render(context, request))


def verify_owner_email(request, owner_id):
    template = loader.get_template(template_ids['verify_email_view'])
    return OwnerViewsHandler.verify_owner_email(request=request, owner_id=owner_id,
                                                template=template)


def forget_password(request):
    logout(request)
    template = loader.get_template(template_ids['forget_pass_view'])
    return OwnerViewsHandler.forget_password(request=request, template=template)


def success_password_email_view(request):
    template = loader.get_template(template_ids['success_password_email'])
    context = {}
    return HttpResponse(template.render(context, request))


def login(request):
    """General login function

      Parameters
      ----------
      request

      Returns
      -------

    """
    template = loader.get_template(template_ids['login'])

    if request.method == 'POST':
        form = OwnerLogin(request.POST)

        if form.is_valid():
            return OwnerViewsHandler.login_owner(request=request, template=template)
        else:

            form = SurveyorLogin(request.POST)
            if form.is_valid():
                print("Loging in surveyor")
                return SurveyorViewHandler.login_surveyor(request, template=template)
    else:

        #user = User.objects.create_user(username="a.giavaras@gmail.com",
        #                                password="123_",
        #                                email="a.giavaras@gmail.com",
        #                                first_name="Alex", last_name="Giavaras")
        #user.save()
        context = {}
        return HttpResponse(template.render(context, request))


def logout_user(request):
    logout(request)
    return redirect('/')


def my_settings_view(request, owner_id: str):
    template = loader.get_template(template_ids['my_settings_view'])
    context = {'user_auth': True, 'owner_id': owner_id}
    return HttpResponse(template.render(context, request))


@login_required(login_url='/login/')
def owner_profile(request, owner_id: str):
    """Renders the owner profile

      Parameters
      ----------
      request

      Returns
      -------
    """

    template = loader.get_template(template_ids['owner_profile'])
    return OwnerViewsHandler.owner_profile(request=request, owner_id=owner_id, template=template)


@login_required(login_url='/login/')
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
    response = OwnerViewsHandler.delete_owner(request=request, owner_id=owner_id)
    logout(request=request)
    return response


@login_required(login_url='/login/')
def subscription_view(request, owner_id: str):
    template = loader.get_template(template_ids['my_subscription_view'])
    return OwnerViewsHandler.subscription_view(request=request, owner_id=owner_id, template=template)


@login_required(login_url='/login/')
def buy_subscription_view(request, owner_id: str, subscription_type: str):
    template = loader.get_template(template_ids['buy_subscription_view'])
    return SubscriptionsViewHandler.buy_subscription_view(request=request, owner_id=owner_id,
                                                          subscription_type=subscription_type, template=template)


@login_required(login_url='/login/')
def not_valid_subscription_view(request, owner_id: str):
    template = loader.get_template(template_ids['not_valid_subscription_view'])
    return SubscriptionsViewHandler.not_valid_subscription_view(request=request,
                                                                owner_id=owner_id, template=template)


@login_required(login_url='/login/')
def vessel_registration(request, owner_id: str):
    """Register a vessel for the given owner

      Parameters
      ----------
      request
      owner_id: The owner id this vessel belongs to

      Returns
      -------

    """
    template = loader.get_template(template_ids['vessel_registration'])
    return VesselViewsHandler.vessel_registration(request=request, owner_id=owner_id,
                                                  template=template)


@login_required(login_url='/login/')
def vessel_profile(request, owner_id: str, vessel_id: str):
    template = loader.get_template(template_ids['vessel_profile'])
    return VesselViewsHandler.vessel_profile(request=request, owner_id=owner_id,
                                             vessel_id=vessel_id, template=template)


@login_required(login_url='/login/')
def vessel_surveys_in_progress_view(request, owner_id: str, vessel_id: str):
    template = loader.get_template(template_ids['vessel_survey_progress'])
    return SurveyViewHandler.vessel_surveys_in_progress_view(request=request, owner_id=owner_id,
                                                             vessel_id=vessel_id, template=template)


@login_required(login_url='/login/')
def generate_survey_view(request, owner_id: str, vessel_id: str):
    """Renders the generate survey view

    Parameters
    ----------
    request
    owner_id: The id of the owner
    vessel_id: The vessel id

    Returns
    -------

    """

    template = loader.get_template(template_ids['generate_survey_view_template'])
    return SurveyViewHandler.generate_survey(request=request, owner_id=owner_id, vessel_id=vessel_id,
                                              surveys_path=SURVEYS_PATH, template=template)


@login_required(login_url='/login/')
def generate_condition_survey_view(request, owner_id: str, vessel_id: str,  survey_id: str):
    template = loader.get_template(template_ids['generate_condition_survey_view_template'])
    return SurveyViewHandler.generate_condition_survey_view(request=request, owner_id=owner_id, vessel_id=vessel_id,
                                                            survey_id=survey_id, template=template)


@login_required(login_url='/login/')
def vessel_part_survey_parts_view(request, owner_id: str,  survey_id: str, vessel_part_id: str):
    template = loader.get_template(template_ids['vessel_part_survey_parts_view'])
    return SurveyViewHandler.vessel_part_survey_parts_view(request=request, owner_id=owner_id,
                                                           survey_id=survey_id,
                                                           vessel_part_id=vessel_part_id,
                                                           template=template)


@login_required(login_url='/login/')
def take_survey_photo_view(request, owner_id: str, survey_id: str,
                           vessel_part: str,
                           survey_part_id: str):
    template = loader.get_template(template_ids['take_survey_photo_view'])
    return SurveyViewHandler.take_survey_photo_view(request=request, owner_id=owner_id, survey_id=survey_id,
                                                    vessel_part=vessel_part, survey_part_id=survey_part_id,
                                                    surveys_path=SURVEYS_PATH, max_img_counter= TOTAL_IMAGE_COUNTER,
                                                    template=template)


@login_required(login_url='/login/')
def vessel_part_subpart_image_preview(request, owner_id: str, survey_id: str,
                                      vessel_part: str, survey_part_id: str):

    template = loader.get_template(template_ids['image_preview_view'])
    return SurveyViewHandler.vessel_part_subpart_image_preview(request=request, owner_id=owner_id,
                                                               survey_id=survey_id, vessel_part=vessel_part,
                                                               survey_part_id=survey_part_id,
                                                               max_img_counter=TOTAL_IMAGE_COUNTER,
                                                               template=template)


@login_required(login_url='/login/')
def owner_view_photo(request, owner_id: str, survey_id: str, vessel_part: str,
                     survey_part_id: str, photo_id: str):
    template = loader.get_template(template_ids['owner_photo_view'] )
    return SurveyViewHandler.view_photo(request=request, owner_id=owner_id, survey_id=survey_id,
                                        survey_part_id=survey_part_id, vessel_part=vessel_part,
                                        image_id=photo_id,
                                        template=template)


@login_required(login_url='/login/')
def submit_vessel_subpart_images(request, survey_id:str, owner_id:str,
                                 vessel_id: str, survey_part_id: str):

    return SurveyViewHandler.submit_vessel_subpart_images(request=request, survey_id=survey_id, owner_id=owner_id,
                                                          vessel_id=vessel_id, survey_part_id=survey_part_id)


@login_required(login_url='/login/')
def view_owner_survey_requests(request, owner_id: str):
    template = loader.get_template(template_ids['owner_survey_requests_view'])
    return OwnerViewsHandler.view_owner_survey_requests(request=request, owner_id=owner_id, template=template)


@login_required(login_url='/login/')
def delete_owner_vessel_survey(request, owner_id: str, survey_id: str):
    # find the owner via email
    url = MIR_APP_REST_API + f'surveys/{survey_id}/'
    response = requests.delete(url=url)
    return redirect(to=f'/owner/{owner_id}/surveys/')


@login_required(login_url='/login/')
def view_owner_survey_request_summary(request, owner_id: str, vessel_id, survey_id: str):

    template = loader.get_template(template_ids['owner_survey_summary_view'])
    return SurveyViewHandler.view_owner_survey_request_summary(request=request,
                                                               owner_id=owner_id, vessel_id=vessel_id,
                                                               survey_id=survey_id, template=template)


@login_required(login_url='/login/')
def submit_photos(request, owner_id: str, vessel_id: str, survey_id: str, vessel_part: str, vessel_subpart: str):
    return generate_condition_survey_view(request, owner_id, vessel_id, survey_id)


@login_required(login_url='/login/')
def submit_survey(request, owner_id: str, vessel_id: str, survey_id: str):
    return SurveyViewHandler.submit_survey(request=request, owner_id=owner_id,
                                           vessel_id=vessel_id, survey_id=survey_id)


@login_required(login_url='/login/')
def delete_survey_from_vessel(request, owner_id: str, vessel_id: str, survey_id: str):
    template = loader.get_template(template_ids['delete_survey_from_vessel_view'])
    return SurveyViewHandler.delete_survey_from_vessel(request=request,
                                                       owner_id=owner_id,
                                                       vessel_id=vessel_id,
                                                       survey_id=survey_id,
                                                       template=template)


@login_required(login_url='/login/')
def survey_part_summary_view(request, survey_id, vessel_part):
    template = loader.get_template(template_ids['survey_part_summary_view'])
    return SurveyViewHandler.survey_part_summary_view(request=request, survey_id=survey_id,
                                                      vessel_part=vessel_part,
                                                      template=template)


@login_required(login_url='/login/')
def download_survey(request, owner_id: str, survey_id: str, filename='survey.pdf') -> HttpResponse:

    return SurveyViewHandler.download_survey(request=request, owner_id=owner_id,
                                             survey_id=survey_id, filename=filename)

@login_required(login_url='/login/')
def owner_survey_vessel_part_no_5(request, owner_id: str,
                                      survey_id: str, vessel_id: str,
                                      vessel_part_id: str):
    return SurveyViewHandler.owner_survey_vessel_part_no_5(request=request,
                                                           owner_id=owner_id, survey_id=survey_id,
                                                           vessel_id=vessel_id, vessel_part_id=vessel_part_id)


def verify_surveyor_email(request, surveyor_id: str):

    if request.method == 'POST':

        url = MIR_APP_REST_API + f'surveyors/signup/{surveyor_id}/confirm'
        post_data = json.dumps({'verification_code': str(request.POST.get('code'))})

        response = requests.post(url=url, data=post_data)
        return redirect('/login/')
    else:

        template = loader.get_template(template_ids['verify_surveyor_email_view'])
        context = {'surveyor_id': surveyor_id}
        return HttpResponse(template.render(context, request))


@login_required(login_url='/login/')
def surveyor_profile(request, surveyor_id: str):
    template = loader.get_template(template_ids['surveyor_profile'])
    return SurveyorViewHandler.surveyor_profile(request=request,
                                                surveyor_id=surveyor_id, template=template)


@login_required(login_url='/login/')
def surveyor_settings_view(request, surveyor_id: str):
    template = loader.get_template(template_ids['surveyor_settings_view'])
    return SurveyorViewHandler.surveyor_settings_view(request=request, surveyor_id=surveyor_id,
                                                      template=template)


@login_required(login_url='/login/')
def surveyor_survey_view(request, surveyor_id: str, survey_id: str):
    template = loader.get_template(template_ids['surveyor_survey_view'])
    return SurveyorViewHandler.surveyor_survey_view(request=request, surveyor_id=surveyor_id,
                                                    survey_id=survey_id, template=template)


@login_required(login_url='/login/')
def surveyor_start_survey_view(request, surveyor_id: str, survey_id: str):
    template = loader.get_template(template_ids['surveyor_survey_content_view'])
    return SurveyorViewHandler.surveyor_start_survey_view(request=request,
                                                          surveyor_id=surveyor_id,
                                                          survey_id=survey_id,
                                                          template=template)


@login_required(login_url='/login/')
def surveyor_survey_part_view(request, surveyor_id: str, survey_id: str, vessel_part_id: str):
    template = loader.get_template(template_ids['surveyor_survey_part_view'])
    return SurveyorViewHandler.surveyor_survey_part_view(request=request, surveyor_id=surveyor_id,
                                                         survey_id=survey_id,
                                                         vessel_part_id=vessel_part_id,
                                                         template=template)


@login_required(login_url='/login/')
def surveyor_survey_subpart_images_preview_view(request, surveyor_id:str,
                                                survey_id: str, vessel_part_id: str, vessel_subpart_id: str):
    template = loader.get_template(template_ids['surveyor_vessel_part_subpart_images'])
    return SurveyorViewHandler.surveyor_vessel_part_subpart_images(request=request, surveyor_id=surveyor_id,
                                                                   survey_id=survey_id, vessel_part_id=vessel_part_id,
                                                                   vessel_subpart_id=vessel_subpart_id, template=template)


@login_required(login_url='/login/')
def survey_report_write(request, surveyor_id: str, survey_id: str, page: int):
    return SurveyorViewHandler.survey_report_write(request=request, surveyor_id=surveyor_id,
                                                   survey_id=survey_id, page=page)

"""
@login_required(login_url='/login/')
def surveyor_vessel_part_subpart_images(request, surveyor_id: str,
                                        survey_id: str, vessel_part: str,
                                        vessel_subpart: str):

    template = loader.get_template(template_ids['surveyor_vessel_part_subpart_images'])
    return SurveyorViewHandler.surveyor_vessel_part_subpart_images(request=request, surveyor_id=surveyor_id,
                                                                   survey_id=survey_id, vessel_part=vessel_part,
                                                                   vessel_subpart=vessel_subpart, template=template)
"""

@login_required(login_url='/login/')
def surveyor_photo_view(request, surveyor_id: str, survey_id,
                        vessel_part: str, vessel_subpart: str,
                        img_url: str):
    template = loader.get_template(template_ids['surveyor_photo_view_template'])

    img_url_final = survey_id + '/' + vessel_part + '/' + vessel_subpart + '/' + img_url

    context = {'user_auth': True,
               'user_surveyor_auth': True, 'surveyor_id': surveyor_id,
               'survey_id': survey_id, 'vessel_part': vessel_part,
               'vessel_subpart': vessel_subpart,
               'img_url': img_url_final, 'media_url': MEDIA_URL,
               'img_file_name': img_url
               }

    return HttpResponse(template.render(context, request))


@login_required(login_url='/login/')
def delete_surveyor(request, surveyor_id: str):
    """Handles the delete view

       Parameters
       ----------
       request
       surveyor_id: The id of the owner to delete

       Returns
       -------
       An instance of HttpResponse
       """

    # find the owner via email
    url = MIR_APP_REST_API + f'surveyors/{surveyor_id}'
    response = requests.delete(url=url)
    return redirect(to='/login/')


@login_required(login_url='/login/')
def submit_survey_surveyor(request, surveyor_id: str, survey_id: str):
    """Submits the survey from the surveyor side

    Parameters
    ----------
    request
    surveyor_id
    survey_id

    Returns
    -------

    """
    url = MIR_APP_REST_API + f'surveys/{survey_id}/submit/?surveyor_idx={surveyor_id}'
    response = requests.patch(url=url)
    return redirect(to=f'/surveyor/{surveyor_id}/dashboard/')



















