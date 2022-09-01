import mimetypes
import json
from pathlib import Path
import requests
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet



from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect
from django.http import Http404

from mir_web_app_demo.settings import MEDIA_URL

from mir_app.forms import OwnerLogin
from mir_app.forms import SurveyorLogin

from mir_app.forms import VesselRegistration
from mir_app.utils import create_survey_directory
from mir_app.utils import save_image
from mir_app.utils import count_number_of_files
from mir_app.form_handlers import handle_vessel_registration
from mir_app.form_handlers import handle_generate_survey
from mir_app.form_handlers import handle_uploaded_img
from mir_app.form_handlers import handle_owner_signup
from mir_app.form_handlers import handle_surveyor_signup


# Create your views here.

template_ids = dict()
template_ids['index'] = 'mir_app/index.html'
template_ids['terms_and_conditions'] = 'mir_app/t_and_c.html'
template_ids['pricing'] = 'mir_app/pricing.html'
template_ids['about'] = 'mir_app/about.html'
template_ids['login'] = 'mir_app/login.html'
template_ids['signup'] = 'mir_app/signup.html'
template_ids['verify_email_view'] = 'mir_app/verify_email_view_template.html'
template_ids['forget_pass_view'] = 'mir_app/forget_pass_view_template.html'
template_ids['contact'] = 'mir_app/contact.html'
template_ids['data_privacy_view'] = 'mir_app/data_privacy_view_template.html'

template_ids['owner_profile'] = 'mir_app/owner/owner_profile.html'
template_ids['vessel_profile'] = 'mir_app/owner/vessel_profile.html'
template_ids['my_settings_view'] = 'mir_app/owner/my_settings_view_template.html'
template_ids['vessel_registration'] = 'mir_app/owner/register_vessel.html'
template_ids['buy_subscription_view'] = 'mir_app/owner/buy_subscription_view_template.html'
template_ids['vessel_survey_progress'] = 'mir_app/owner/vesssel_survey_in_progress.html'
template_ids['generate_survey_view_template'] = 'mir_app/owner/generate_survey_view_template.html'
template_ids['owner_survey_requests_view'] = 'mir_app/owner/owner_survey_requests_view_template.html'

template_ids['delete_survey_from_vessel_view'] = 'mir_app/owner/vessel/delete_survey_from_vessel_view.html'

template_ids['generate_condition_survey_view_template'] = 'mir_app/generate_condition_survey_view_template.html'
template_ids['take_survey_photo_view'] = 'mir_app/owner/take_survey_photo_view_template.html'
template_ids['image_preview_view'] = 'mir_app/image_preview_view_template.html'

template_ids['owner_survey_summary_view'] = 'mir_app/owner/survey_summary_template.html'
template_ids['survey_part_summary_view'] = 'mir_app/owner/survey_part_summary_template.html'
template_ids['my_subscription_view'] = 'mir_app/owner/my_subscription_template.html'

# surveyor view
template_ids['verify_surveyor_email_view'] = 'mir_app/surveyor/verify_surveyor_email_view_template.html'

template_ids['surveyor_profile'] = 'mir_app/surveyor/surveyor_profile.html'
template_ids['surveyor_settings_view'] = 'mir_app/surveyor/surveyor_settings_view_template.html'
template_ids['surveyor_survey_view'] = 'mir_app/surveyor/surveyor_survey_view_template.html'
template_ids['surveyor_vessel_part_subpart_images'] = 'mir_app/surveyor/surveyor_vessel_part_subpart_images_template.html'
template_ids['surveyor_photo_view_template'] = 'mir_app/surveyor/surveyor_photo_view_template.html'
template_ids['surveyor_survey_content_view'] = 'mir_app/surveyor/surveyor_survey_content_view_template.html'

template_ids['page_not_found_handler'] = '404.html'
template_ids['server_error_handler'] = '500.html'


MIR_APP_REST_API = 'http://127.0.0.1:8000/api/v1/'
#SURVEY_ID = "123"
SURVEYS_PATH = Path("/home/alex/qi3/mir_app_web_app/surveys")
OWNER_ID = '6306179d0eb28a571d11c282'
TOTAL_IMAGE_COUNTER = 5


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
    context = {'owner_id': OWNER_ID, 'Pro': 'Pro',
               'Enterprise': 'Enterprise', 'Free': 'Free'}
    return HttpResponse(template.render(context, request))


def contact(request):
    template = loader.get_template(template_ids['contact'])
    context = {}
    return HttpResponse(template.render(context, request))


def signup(request):

    if request.method == 'POST':

        try:
            form_data = handle_owner_signup(request=request)
        except ValueError:
            form_data = handle_surveyor_signup(request=request)

        if 'owner_name' in form_data:

            # send the data to the DB
            url = MIR_APP_REST_API + 'owners/signup'

            owner_email = form_data['owner_email']
            owner_password = form_data['owner_password']
            name = form_data['owner_name']
            surname = form_data['owner_surname']

            post_data = json.dumps({'name': name, 'surname': surname,
                                    'email': owner_email, 'password': owner_password})

            response = requests.post(url=url, data=post_data)
            response = response.json()

            idx = response['idx']
            return redirect(to=f'/owner/{idx}/verify-email/')
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

        # does the user exist
    else:

        template = loader.get_template(template_ids['signup'])
        context = {}
        return HttpResponse(template.render(context, request))


def verify_owner_email(request, owner_id):

    if request.method == 'POST':

        url = MIR_APP_REST_API + f'owners/signup/{owner_id}/confirm'
        post_data = json.dumps({'verification_code': str(request.POST.get('code'))})

        response = requests.post(url=url, data=post_data)
        return redirect('/login/')
    else:

        template = loader.get_template(template_ids['verify_email_view'])
        context = {'owner_id': owner_id}
        return HttpResponse(template.render(context, request))


def forget_password(request):

    if request.method == 'POST':
        return redirect(to='/login/')
    else:
        template = loader.get_template(template_ids['forget_pass_view'])
        context = {}
        return HttpResponse(template.render(context, request))


def data_privacy_view(request):
    template = loader.get_template(template_ids['data_privacy_view'])
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

    if request.method == 'POST':

        form = OwnerLogin(request.POST)

        if form.is_valid():
            return login_owner(request)
        else:
            form = SurveyorLogin(request.POST)

            if form.is_valid():
                return login_surveyor(request)

    else:

        template = loader.get_template(template_ids['login'])
        context = {}
        return HttpResponse(template.render(context, request))


def login_owner(request):
    """Login the owner

      Parameters
      ----------
      request

      Returns
      -------

    """

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

            response_json = response.json()
            owner_id = response_json['idx']
            return redirect(to=f'/owner/{owner_id}/dashboard/')

    template = loader.get_template(template_ids['index'])
    context = {}
    return HttpResponse(template.render(context, request))


def login_surveyor(request):

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

            return redirect(to=f'/surveyor/{surveyor_id}/dashboard/')
        else:
            raise ValueError("Form is not valid")

    template = loader.get_template(template_ids['index'])
    context = {}
    return HttpResponse(template.render(context, request))


def logout(request):
    return redirect('/')


def my_settings_view(request, owner_id: str):
    template = loader.get_template(template_ids['my_settings_view'])
    context = {'user_auth': True, 'owner_id': owner_id}
    return HttpResponse(template.render(context, request))


def owner_profile(request, owner_id: str):
    """Renders the owner profile

      Parameters
      ----------
      request

      Returns
      -------
    """

    template = loader.get_template(template_ids['owner_profile'])

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


def subscription_view(request, owner_id: str):
    template = loader.get_template(template_ids['my_subscription_view'])

    url = MIR_APP_REST_API + f'owners/{owner_id}'
    response = requests.get(url=url)
    response = response.json()

    context = {'user_auth': True,
               'owner_id': owner_id,
               'subscription_type': response['subscription_plan_id']}
    return HttpResponse(template.render(context, request))


def buy_subscription_view(request, owner_id: str, subscription_type: str):
    template = loader.get_template(template_ids['buy_subscription_view'])
    context = {'user_auth': True, 'owner_id': owner_id, 'subscription_type': subscription_type}
    return HttpResponse(template.render(context, request))


def vessel_registration(request, owner_id: str):
    """Register a vessel for the given owner

      Parameters
      ----------
      request
      owner_id: The owner id this vessel belongs to

      Returns
      -------

    """

    if request.method == 'POST':
        response = handle_vessel_registration(request, owner_id)

        # register the vessel
        response_json = response.json()
        return redirect(f'/owner/{owner_id}/vessel-profile/{response_json["idx"]}')
    else:
        # get the vessel types

        url = MIR_APP_REST_API + f'vessels/types?user_token={owner_id}'
        response = requests.get(url=url)
        response_json = response.json()
        print(response_json)

        template = loader.get_template(template_ids['vessel_registration'])
        context = {'user_auth': True, 'owner_id': owner_id,
                   'vessel_types': response_json}
        return HttpResponse(template.render(context, request))


def vessel_profile(request, owner_id: str, vessel_id: str):
    template = loader.get_template(template_ids['vessel_profile'])

    url = MIR_APP_REST_API + f'vessels/{vessel_id}/?mmsi=false&ce=false'

    # retrieve the vessel data
    response = requests.get(url=url, data=json.dumps({}))
    response_json = response.json()

    context = {'user_auth': True,
               'owner_id': owner_id, 'vessel_id': vessel_id}
    context.update(response_json)
    context['vessel_name'] = context['name']
    return HttpResponse(template.render(context, request))


def vessel_surveys_in_progress_view(request, owner_id: str, vessel_id: str, vessel_name: str):
    template = loader.get_template(template_ids['vessel_survey_progress'])

    # get the surveys that are in progress
    # for this vessel and this owner
    url = MIR_APP_REST_API + f"surveys/?vessel_id={vessel_id}"
    response = requests.get(url=url)
    response_json = response.json()

    in_progress_surveys = []
    pending_surveys = []
    completed_surveys_reqs = []
    for survey in response_json:
        if survey['owner_survey_status'] == 'IN_PROGRESS':
            in_progress_surveys.append((survey['idx'], survey['survey_type'],
                                        survey['created_at'].split(" ")[0], 'IN_PROGRESS'))
        elif survey['owner_survey_status'] == 'COMPLETED' and survey['survey_request_status'] == 'PENDING':
            pending_surveys.append((survey['idx'], survey['survey_type'],
                                    survey['created_at'].split(" ")[0], survey['survey_request_status']))
        elif survey['owner_survey_status'] == 'COMPLETED' and survey['survey_request_status'] == 'COMPLETED':
            completed_surveys_reqs.append((survey['idx'], survey['survey_type'],
                                           survey['created_at'].split(" ")[0], survey['survey_request_status']))

    context = {'user_auth': True, 'owner_id': owner_id,
               'vessel_id': vessel_id,
               'in_progress_surveys': in_progress_surveys,
               'pending_surveys_reqs': pending_surveys,
               'completed_surveys_reqs': completed_surveys_reqs,
               'vessel_name': vessel_name}
    return HttpResponse(template.render(context, request))


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

    # get the available survey types
    url = MIR_APP_REST_API + f'surveys/surveys-types'
    response = requests.get(url=url)
    response_json = response.json()

    if request.method == 'POST':

        data = handle_generate_survey(request,
                                      owner_id=owner_id, vessel_id=vessel_id)

        # create the surveu
        url = MIR_APP_REST_API + f'surveys/'

        post_data = {"owner_idx": owner_id,
                     "vessel_idx": vessel_id,
                     "survey_type": "CONDITIONAL_SURVEY"}

        response = requests.post(url=url, data=json.dumps(post_data))
        response_json = response.json()
        survey_id = response_json['idx']

        try:
            # create the survey directory
            create_survey_directory(directory_path=SURVEYS_PATH, survey_id=survey_id)
        except ValueError as e:
            print(str(e))

        return redirect(to=f'/owner/{owner_id}/vessel/{vessel_id}/surveys/condition-survey/{survey_id}/')

    template = loader.get_template(template_ids['generate_survey_view_template'])
    context = {'user_auth': True, 'owner_id': owner_id, 'vessel_id': vessel_id,
               'survey_types': response_json}

    return HttpResponse(template.render(context, request))


def generate_condition_survey_view(request, owner_id: str, vessel_id: str,  survey_id: str):

    url = MIR_APP_REST_API + f'surveys/condition_survey/rib/vessel_parts'

    response = requests.get(url=url)
    response_json = response.json()

    print(response_json['vessel_parts'])
    vessel_parts = [[item['vessel_part'],  item['vessel_sub_parts']] for item in response_json['vessel_parts']]

    for i, item in enumerate(vessel_parts):

        vessel_part = item[0]
        vessel_part = vessel_part.replace(' ', '-')

        item[0] = vessel_part

        vessel_subparts = item[1]

        for j, subpart in enumerate(vessel_subparts):
            subpart = subpart.replace(' ', '-')
            vessel_subparts[j] = subpart

        vessel_parts[i] = [item[0], vessel_subparts]

    template = loader.get_template(template_ids['generate_condition_survey_view_template'])
    context = {'user_auth': True, 'owner_id': owner_id, 'vessel_id': vessel_id,
               'survey_id': survey_id,
               'vessel_parts': vessel_parts}

    return HttpResponse(template.render(context, request))


def take_survey_photo_view(request, survey_id: str, owner_id: str,
                           vessel_id: str, vessel_part: str, vessel_subpart: str):

    if request.method == 'POST':

        form_data = handle_uploaded_img(request, survey_id, owner_id,
                                        vessel_id, vessel_part, vessel_subpart)

        # count how many images do we have

        img_filename = form_data['image'].name

        image_path = Path(SURVEYS_PATH / survey_id / vessel_part / vessel_subpart)
        images = count_number_of_files(filepath=image_path, postfix=['jpg', 'png', 'jpeg'])

        img_counter = len(images)

        img_filename = vessel_subpart + "_img_" + str(img_counter + 1) + "." + img_filename.split(".")[-1]

        # save the image
        image_path = Path(SURVEYS_PATH / survey_id / vessel_part / vessel_subpart / img_filename)
        save_image(form_data['image'], filepath=image_path)

        if img_counter + 1 == TOTAL_IMAGE_COUNTER:
            return redirect(f'/surveys/condition-survey/{owner_id}/{vessel_id}/{survey_id}/{vessel_part}/{vessel_subpart}/image_preview')

        else:

            template = loader.get_template(template_ids['take_survey_photo_view'])
            context = {'user_auth': True, 'owner_id': owner_id, 'vessel_id': vessel_id,
                       'survey_id': survey_id, 'vessel_part': vessel_part,
                       'vessel_subpart': vessel_subpart,
                       'img_counter': img_counter + 1, "total_img_counter": TOTAL_IMAGE_COUNTER}

            return HttpResponse(template.render(context, request))

    else:

        try:
            # save the image to the surveys
            create_survey_directory(directory_path=SURVEYS_PATH / survey_id, survey_id=vessel_part)
            create_survey_directory(directory_path=SURVEYS_PATH / survey_id / vessel_part, survey_id=vessel_subpart)
        except ValueError as e:
            print(str(e))

        image_path = SURVEYS_PATH / survey_id / vessel_part / vessel_subpart
        images = count_number_of_files(filepath=image_path, postfix=['jpg', 'png', 'jpeg'])
        print(images)

        template = loader.get_template(template_ids['take_survey_photo_view'])
        context = {'user_auth': True, 'owner_id': owner_id, 'vessel_id': vessel_id,
                   'survey_id': survey_id, 'vessel_part': vessel_part,
                   'vessel_subpart': vessel_subpart,
                   'img_counter': len(images), "total_img_counter": TOTAL_IMAGE_COUNTER}

        return HttpResponse(template.render(context, request))


def vessel_part_subpart_image_preview(request, owner_id: str, vessel_id: str, survey_id: str, vessel_part: str, vessel_subpart: str):
    template = loader.get_template(template_ids['image_preview_view'])

    # collect the images
    image_path = SURVEYS_PATH / survey_id / vessel_part / vessel_subpart
    tmp_images = count_number_of_files(filepath=image_path, postfix=['jpg', 'png', 'jpeg'])

    images = []
    for img in tmp_images:
        img = str(img)
        img_details = img.split("/")
        img = survey_id + "/" + vessel_part + "/" + vessel_subpart + "/" + img_details[-1]
        images.append(img)

    context = {'user_auth': True, 'owner_id': owner_id, 'vessel_id': vessel_id,
               'survey_id': survey_id, 'vessel_part': vessel_part,
               'vessel_subpart': vessel_subpart,
               'img_counter': len(images), "total_img_counter": TOTAL_IMAGE_COUNTER,
               'images': images, 'media_url': MEDIA_URL}

    return HttpResponse(template.render(context, request))


def view_owner_survey_requests(request, owner_id: str):
    template = loader.get_template(template_ids['owner_survey_requests_view'])

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
        # get the vessel name that corresponds to this
        # survey
        vessel_id = survey_response_json['vessel_idx']

        context['vessel_id'] = vessel_id

        url = MIR_APP_REST_API + f'vessels/{vessel_id}/'

        response = requests.get(url=url)
        vessel_response_json = response.json()

        if survey_response_json['owner_survey_status'] == "IN_PROGRESS":
            in_progress_surveys.append((survey, vessel_response_json['name'],
                                        survey_response_json['survey_type'],
                                        survey_response_json['created_at'].split(" ")[0],
                                        "IN PROGRESS"))
        elif survey_response_json['survey_request_status'] == "PENDING":
            pending_surveys_req.append((survey, vessel_response_json['name'],
                                        survey_response_json['survey_type'],
                                        survey_response_json['created_at'].split(" ")[0],
                                        'PENDING'))
        elif survey_response_json['survey_request_status'] == "IN_PROGRESS":
            in_progress_surveys_req.append((survey, vessel_response_json['name'],
                                            survey_response_json['survey_type'],
                                            survey_response_json['created_at'].split(" ")[0],
                                            "IN_PROGRESS"))
        elif survey_response_json['survey_request_status'] == "COMPLETED":
            completed_surveys_reqs.append((survey, vessel_response_json['name'],
                                          survey_response_json['survey_type'],
                                          survey_response_json['created_at'].split(" ")[0],
                                           "COMPLETED"))

    context['in_progress_surveys'] = in_progress_surveys
    context['pending_surveys_reqs'] = pending_surveys_req
    context['in_progress_surveys_reqs'] = in_progress_surveys_req
    context['completed_surveys_reqs'] = completed_surveys_reqs

    return HttpResponse(template.render(context, request))


def delete_owner_vessel_survey(request, owner_id: str, survey_id: str):
    # find the owner via email
    url = MIR_APP_REST_API + f'surveys/{survey_id}/'
    response = requests.delete(url=url)
    return redirect(to=f'/owner/{owner_id}/surveys/')


def view_owner_survey_request_summary(request, owner_id: str, vessel_id, survey_id: str):

    template = loader.get_template(template_ids['owner_survey_summary_view'])

    # in the surveys list get the surveys that correspond to this owner
    # stack them as completed, in_progress, pending
    surveys = ["AlexBlue-CONDITION_SURVEY-08.2022-123"]

    executive_summary = "Lorem ipsum dolor sit amet consectetur adipisicing elit. \
                                Iusto est, ut esse a labore aliquam beatae expedita. Blanditiis impedit numquam libero molestiae \
                                et fugit cupiditate, quibusdam expedita, maiores eaque quisquam."

    context = {'user_auth': True, 'survey_requests': surveys,
               "executive_summary": executive_summary,
               'owner_id': owner_id, 'survey_id': survey_id, 'vessel_part': "Hull"}
    return HttpResponse(template.render(context, request))


def submit_photos(request, owner_id: str, vessel_id: str, survey_id: str, vessel_part: str, vessel_subpart: str):
    return generate_condition_survey_view(request, owner_id, vessel_id, survey_id)


def submit_survey(request, owner_id: str, vessel_id: str, survey_id: str):

    # we need to let the back-end that the survey is to be submitted

    # find the owner via email
    url = MIR_APP_REST_API + f'surveys/{survey_id}/submit'
    print(url)
    response = requests.patch(url=url)
    response_json = response.json()

    url = MIR_APP_REST_API + f'vessels/{vessel_id}/'
    response = requests.get(url=url)
    response_json = response.json()

    return redirect(f'/owner/{owner_id}/vessel-profile/{vessel_id}/{response_json["name"]}/in-progress-surveys/')


def delete_survey_from_vessel(request, owner_id: str, vessel_id: str, survey_id: str):

    if request.method == 'POST':

        # find the owner via email
        url = MIR_APP_REST_API + f'surveys/{survey_id}/'
        print(url)
        response = requests.delete(url=url)
        response_json = response.json()

        url = MIR_APP_REST_API + f'vessels/{vessel_id}/'
        response = requests.get(url=url)
        response_json = response.json()

        return redirect(f'/owner/{owner_id}/vessel-profile/{vessel_id}/{response_json["name"]}/in-progress-surveys/')
    else:

        template = loader.get_template(template_ids['delete_survey_from_vessel_view'])
        context = {'owner_id': owner_id, 'vessel_id': vessel_id, 'survey_id': survey_id}
        return HttpResponse(template.render(context, request))


def survey_part_summary_view(request, survey_id, vessel_part):
    template = loader.get_template(template_ids['survey_part_summary_view'])
    context = {'vessel_part': vessel_part}
    return HttpResponse(template.render(context, request))


def download_survey(request, owner_id: str, survey_id: str, filename='survey.pdf') -> HttpResponse:

        #filename = 'survey.pdf'
        result_filename = SURVEYS_PATH / survey_id /'survey.pdf'

        doc = SimpleDocTemplate(
            str(result_filename),
            pagesize=letter,
            rightMargin=72, leftMargin=72,
            topMargin=72, bottomMargin=18,
            title=f"Survey ID: {survey_id}",
            author="Surveyor: Alexandros Giavaras, Licence no: 007\n"
        )
        styles = getSampleStyleSheet()
        flowables = []

        paragraph_1 = Paragraph(f"Survey ID: {survey_id}", styles['Heading1'])
        paragraph_2 = Paragraph("Surveyor: Alexandros Giavaras, Licence no: 007", styles['BodyText'])

        text = "This report was generated by the mir platform at 28/08/2022"
        para = Paragraph(text, style=styles["Normal"])
        flowables.append(paragraph_1)
        flowables.append(paragraph_2)
        flowables.append(para)
        doc.build(flowables)

        # Set the mime type
        mime_type, _ = mimetypes.guess_type(filename)

        try:
            # open file for read
            path = open(result_filename, 'rb')
        except Exception as e:
            raise Http404(str(e))

        # Set the return value of the HttpResponse
        response = HttpResponse(path, content_type='application/pdf')

        # Set the HTTP header for sending to browser
        response['Content-Disposition'] = "attachment; filename=%s" % filename
        path.close()
        return response


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


def surveyor_profile(request, surveyor_id: str):
    template = loader.get_template(template_ids['surveyor_profile'])

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

        if survey_response['owner_survey_status'] == 'COMPLETED' and \
            survey_response['survey_request_status'] == 'PENDING':

            vessel_url = MIR_APP_REST_API + f'vessels/{survey_response["vessel_idx"]}/?mmsi=true&ce=true'
            vessel_response = requests.get(url=vessel_url)

            vessel_response = vessel_response.json()

            pending_surveys.append((vessel_response['name'],
                                    survey_response['survey_type'],
                                    survey_response['created_at'].split(" ")[0],
                                    survey_response['idx'],
                                    survey_response['survey_request_status']))

        elif survey_response['owner_survey_status'] == 'COMPLETED' and \
            survey_response['survey_request_status'] == 'IN_PROGRESS':

            vessel_url = MIR_APP_REST_API + f'vessels/{survey_response["vessel_idx"]}/?mmsi=true&ce=true'
            vessel_response = requests.get(url=vessel_url)

            in_progress_surveys.append((vessel_response['name'],
                                        survey_response['survey_type'],
                                        survey_response['idx'],
                                        survey_response['survey_request_status']))

    surveys = in_progress_surveys + pending_surveys

    context = {'user_auth': True,
               'user_surveyor_auth': True, 'surveyor_name': response_json['name'],
               'surveyor_id': surveyor_id,
               'survey_reqs': surveys}

    return HttpResponse(template.render(context, request))


def surveyor_survey_view(request, surveyor_id: str, survey_id: str):
    template = loader.get_template(template_ids['surveyor_survey_view'])

    # get the survey results

    survey_url = MIR_APP_REST_API + f'surveys/{survey_id}'
    survey_response = requests.get(url=survey_url)

    survey_response = survey_response.json()

    survey_name = survey_response['survey_type']
    request_date = survey_response['created_at'].split(" ")[0]
    survey_request_state = survey_response['survey_request_status']

    context = {'user_auth': True,
               'user_surveyor_auth': True,
               'survey_name': survey_name,
               'request_date': request_date,
               'survey_request_state': survey_request_state,
               'surveyor_id': surveyor_id,
               'survey_id': survey_id,
               'n_total_photos': 15}

    return HttpResponse(template.render(context, request))


def surveyor_vessel_part_subpart_images(request, surveyor_id: str,
                                        survey_id: str, vessel_part: str,
                                        vessel_subpart: str):

    template = loader.get_template(template_ids['surveyor_vessel_part_subpart_images'])

    # collect the images
    image_path = SURVEYS_PATH / survey_id / vessel_part / vessel_subpart
    tmp_images = count_number_of_files(filepath=image_path, postfix=['jpg', 'png', 'jpeg'])

    images = []
    for img in tmp_images:
        img = str(img)
        img_details = img.split("/")
        img = survey_id + "/" + vessel_part + "/" + vessel_subpart + "/" + img_details[-1]
        img_new = img_details[-1] #survey_id + "-" + vessel_part + "-" + vessel_subpart + "-" + img_details[-1]
        images.append((img, img_new))

    print(images)

    context = {'user_surveyor_auth': True, 'surveyor_id': surveyor_id,
               'survey_id': survey_id, 'vessel_part': vessel_part,
               'vessel_subpart': vessel_subpart,
               'img_counter': len(images), "total_img_counter": TOTAL_IMAGE_COUNTER,
               'images': images, 'media_url': MEDIA_URL}

    return HttpResponse(template.render(context, request))


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


def surveyor_settings_view(request, surveyor_id: str):
    template = loader.get_template(template_ids['surveyor_settings_view'])
    context = {'user_auth': True,
               'user_surveyor_auth': True,
               'surveyor_id': surveyor_id}
    return HttpResponse(template.render(context, request))


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


def surveyor_start_survey_view(request, surveyor_id: str, survey_id: str):
    template = loader.get_template(template_ids['surveyor_survey_content_view'])

    url = MIR_APP_REST_API + f'surveys/condition_survey/rib/vessel_parts'

    response = requests.get(url=url)
    response_json = response.json()

    print(response_json['vessel_parts'])
    vessel_parts = [[item['vessel_part'], item['vessel_sub_parts']] for item in response_json['vessel_parts']]

    for i, item in enumerate(vessel_parts):

        vessel_part = item[0]
        vessel_part = vessel_part.replace(' ', '-')

        item[0] = vessel_part

        vessel_subparts = item[1]

        for j, subpart in enumerate(vessel_subparts):

            subpart = subpart.replace(' ', '-')
            vessel_subparts[j] = (subpart, 'PENDING')

        vessel_parts[i] = [item[0], vessel_subparts]

    context = {'user_auth': True,
               'user_surveyor_auth': True,
               'surveyor_id': surveyor_id,
               'vessel_parts': vessel_parts,
               'survey_id': survey_id}
    return HttpResponse(template.render(context, request))


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



















