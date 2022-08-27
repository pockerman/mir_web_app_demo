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


template_ids['owner_profile'] = 'mir_app/owner/owner_profile.html'
template_ids['vessel_profile'] = 'mir_app/owner/vessel_profile.html'
template_ids['vessel_registration'] = 'mir_app/register_vessel.html'
template_ids['buy_subscription_view'] = 'mir_app/owner/buy_subscription_view_template.html'
template_ids['vessel_survey_progress'] = 'mir_app/vesssel_survey_in_progress.html'
template_ids['data_privacy_view'] = 'mir_app/data_privacy_view_template.html'

template_ids['generate_survey_view_template'] = 'mir_app/generate_survey_view_template.html'
template_ids['generate_condition_survey_view_template'] = 'mir_app/generate_condition_survey_view_template.html'
template_ids['take_survey_photo_view'] = 'mir_app/take_survey_photo_view_template.html'
template_ids['image_preview_view'] = 'mir_app/image_preview_view_template.html'
template_ids['owner_survey_requests_view'] = 'mir_app/owner_survey_requests_view_template.html'
template_ids['owner_survey_summary_view'] = 'mir_app/owner/survey_summary_template.html'
template_ids['survey_part_summary_view'] = 'mir_app/owner/survey_part_summary_template.html'
template_ids['my_subscription_view'] = 'mir_app/owner/my_subscription_template.html'

template_ids['surveyor_profile'] = 'mir_app/surveyor/surveyor_profile.html'
template_ids['surveyor_survey_view'] = 'mir_app/surveyor/surveyor_survey_view_template.html'
template_ids['surveyor_vessel_part_subpart_images'] = 'mir_app/surveyor/surveyor_vessel_part_subpart_images_template.html'
template_ids['surveyor_photo_view_template'] = 'mir_app/surveyor/surveyor_photo_view_template.html'

template_ids['page_not_found_handler'] = '404.html'
template_ids['server_error_handler'] = '500.html'


MIR_APP_REST_API = 'http://127.0.0.1:8000/api/v1/'
SURVEY_ID = "123"
SURVEYS_PATH = Path("/home/alex/qi3/mir_web_app_demo/surveys/")
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

        return redirect('/verify-email/')

        # does the user exist
    else:

        template = loader.get_template(template_ids['signup'])
        context = {}
        return HttpResponse(template.render(context, request))


def verify_email(request):

    if request.method == 'POST':
        print("This request is post")
        return redirect('/login/')
    else:

        template = loader.get_template(template_ids['verify_email_view'])
        context = {}
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
            print("owner login is valid")
            return login_owner(request)
        else:

            form = SurveyorLogin(request.POST)

            if form.is_valid():
                print("owner login is valid")
                return login_surveyor(request)

        # does the user exist
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
        print(form.errors)
        print(form.as_ul())
        owner_id = OWNER_ID
        return redirect(to=f'/owner_profile/{owner_id}')

    template = loader.get_template(template_ids['index'])
    context = {}
    return HttpResponse(template.render(context, request))


def login_surveyor(request):

    if request.method == 'POST':
        form = OwnerLogin(request.POST)
        print(form.errors)
        print(form.as_ul())
        owner_id = OWNER_ID
        return redirect(to=f'/surveyor_profile/{owner_id}')

    template = loader.get_template(template_ids['index'])
    context = {}
    return HttpResponse(template.render(context, request))


def logout(request):
    return redirect('/')


def my_settings(request):
    pass


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

    print(vessels)

    if len(vessels) != 0:
        context['vessels'] = vessels
    return HttpResponse(template.render(context, request))


def vessel_profile(request, owner_id: str, vessel_id: str):
    template = loader.get_template(template_ids['vessel_profile'])

    url = MIR_APP_REST_API + f'vessels/{vessel_id}/?mmsi=false&ce=false'

    print(f"Targeting url {url}")
    # retrieve the vessel data
    response = requests.get(url=url, data=json.dumps({}))
    response_json = response.json()

    context = {'user_auth': True, 'owner_id': owner_id}
    context.update(response_json)

    print(context)
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

        response_json = response.json()
        return redirect(f'/vessel_profile/{response_json["idx"]}')
    else:
        # get the vessel types

        url = MIR_APP_REST_API + f'vessels/types?user_token={owner_id}'

        response = requests.get(url=url)
        response_json = response.json()
        print(response_json)
        template = loader.get_template(template_ids['vessel_registration'])
        context = {'user_auth': True, 'owner_idx': owner_id,
                   'vessel_types': response_json}
        return HttpResponse(template.render(context, request))


def surveys_in_progress_view(request, vessel_id: str):
    template = loader.get_template(template_ids['vessel_survey_progress'])
    context = {'user_auth': True}
    return HttpResponse(template.render(context, request))


def subscription_view(request, owner_id: str):
    template = loader.get_template(template_ids['my_subscription_view'])
    context = {'user_auth': True, 'owner_id': owner_id}
    return HttpResponse(template.render(context, request))


def buy_subscription_view(request, owner_id: str, subscription_type: str):
    template = loader.get_template(template_ids['buy_subscription_view'])
    context = {'user_auth': True, 'owner_id': owner_id, 'subscription_type': subscription_type}
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
    url = MIR_APP_REST_API + f'surveys/types'

    response = requests.get(url=url)
    response_json = response.json()

    if request.method == 'POST':

        data = handle_generate_survey(request,
                                      owner_id=owner_id, vessel_id=vessel_id)

        try:
            # create the survey directory
            create_survey_directory(directory_path=SURVEYS_PATH, survey_id=SURVEY_ID)
        except ValueError as e:
            print(str(e))

        # given the survey_type find the appropriate
        # survey handler
        return redirect(f'/surveys/condition-survey/{owner_id}/{vessel_id}/{SURVEY_ID}')

    template = loader.get_template(template_ids['generate_survey_view_template'])
    context = {'user_auth': True, 'owner_id': owner_id, 'vessel_id': vessel_id,
               'survey_types': response_json}

    return HttpResponse(template.render(context, request))


def generate_condition_survey_view(request, owner_id: str, vessel_id: str, survey_id: str):

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


def take_survey_photo_view(request, survey_id: str, owner_id: str, vessel_id: str, vessel_part: str, vessel_subpart: str):

    if request.method == 'POST':

        form_data = handle_uploaded_img(request, survey_id, owner_id, vessel_id, vessel_part, vessel_subpart)

        # count how many images do we have

        img_filename = form_data['image'].name

        image_path = Path(SURVEYS_PATH / SURVEY_ID / vessel_part / vessel_subpart)
        images = count_number_of_files(filepath=image_path, postfix=['jpg', 'png', 'jpeg'])

        img_counter = len(images)

        img_filename = vessel_subpart + "_img_" + str(img_counter + 1) + "." + img_filename.split(".")[-1]

        # save the image
        image_path = Path(SURVEYS_PATH / SURVEY_ID / vessel_part / vessel_subpart / img_filename)
        save_image(form_data['image'], filepath=image_path)

        if img_counter + 1 == TOTAL_IMAGE_COUNTER:
            return redirect(f'/surveys/condition-survey/{owner_id}/{vessel_id}/{SURVEY_ID}/{vessel_part}/{vessel_subpart}/image_preview')

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
            create_survey_directory(directory_path=SURVEYS_PATH / SURVEY_ID, survey_id=vessel_part)
            create_survey_directory(directory_path=SURVEYS_PATH / SURVEY_ID / vessel_part, survey_id=vessel_subpart)
        except ValueError as e:
            print(str(e))

        image_path = SURVEYS_PATH / SURVEY_ID / vessel_part / vessel_subpart
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
    image_path = SURVEYS_PATH / SURVEY_ID / vessel_part / vessel_subpart
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

    # in the surveys list get the surveys that correspond to this owner
    # stack them as completed, in_progress, pending
    surveys = [('COMPLETED', "AlexBlue-CONDITION_SURVEY-08.2022-123", '123'),
               ('PENDING', "Rosa Luxemburg-CLASS_SURVEY-07.2021-2545", "2545")]

    context = {'user_auth': True, 'owner_id': owner_id, 'survey_requests': surveys}
    return HttpResponse(template.render(context, request))


def view_owner_survey_request_summary(request, owner_id: str, survey_id: str):

    print("Iam in view_owner_survey_request_summary")

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
    return redirect(f'/vessel_profile/{owner_id}/{vessel_id}')


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


def surveyor_profile(request, surveyor_id: str):
    template = loader.get_template(template_ids['surveyor_profile'])

    # find the owner via email
    url = MIR_APP_REST_API + f'owners/{surveyor_id}'

    response = requests.get(url=url)
    response_json = response.json()

    surveys = [("AlexBlue-CONDITION_SURVEY-08.2022-123", "123"),
               ("Rosa Luxemburg-CLASS_SURVEY-07.2021-2545", "2545"),
               ("David Hilbert-DAMAGE_SURVEY-05.2020-456fg1", "456fg1")]

    context = {'user_auth': True, 'owner_name': response_json['name'],
               'surveyor_id': surveyor_id,
               'owner_id': response_json['idx'],
               'survey_reqs': surveys}

    return HttpResponse(template.render(context, request))


def surveyor_survey_view(request, surveyor_id: str, survey_id: str):
    template = loader.get_template(template_ids['surveyor_survey_view'])

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
            vessel_subparts[j] = subpart

        vessel_parts[i] = [item[0], vessel_subparts]

    context = {'user_surveyor_auth': True, 'survey_name': "CONDITION SURVEY",
               'request_date': '26.08.2022', 'survey_request_state': 'PENDING',
               'surveyor_id':surveyor_id, 'survey_id': survey_id,
               'vessel_parts': vessel_parts, 'n_total_photos': 15}

    return HttpResponse(template.render(context, request))


def surveyor_vessel_part_subpart_images(request, surveyor_id: str,
                                        survey_id: str, vessel_part: str,
                                        vessel_subpart: str):

    template = loader.get_template(template_ids['surveyor_vessel_part_subpart_images'])

    # collect the images
    image_path = SURVEYS_PATH / SURVEY_ID / vessel_part / vessel_subpart
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

    context = {'user_surveyor_auth': True, 'surveyor_id': surveyor_id,
               'survey_id': survey_id, 'vessel_part': vessel_part,
               'vessel_subpart': vessel_subpart,
               'img_url': img_url_final, 'media_url': MEDIA_URL,
               'img_file_name': img_url
               }

    return HttpResponse(template.render(context, request))
















