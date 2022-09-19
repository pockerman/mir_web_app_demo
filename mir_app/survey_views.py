import json
import requests
from pathlib import Path
from django.shortcuts import redirect
from django.http import HttpResponse
from django.template import loader
from django.http import Http404
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

from mir_app.utils import create_survey_directory
from mir_app.utils import count_number_of_files
from mir_app.form_handlers import handle_uploaded_img
from mir_app.form_handlers import handle_generate_survey
from mir_app.utils import save_image
from mir_web_app_demo.settings import MEDIA_URL
from mir_app.template_views import template_ids

# demo configuration

from mir_app.config import MIR_APP_REST_API
from mir_app.config import SURVEYS_PATH
from mir_app.config import TOTAL_IMAGE_COUNTER
from mir_app.config import MIN_NUM_IMG


def all_item_surveyed(response):
    surveyed_by_owner = True
    for item in response:

        if not surveyed_by_owner:
            break

        for survey_part in item['survey_parts']:

            url = MIR_APP_REST_API + f'items-wrappers/survey-parts/{survey_part}'
            response = requests.get(url=url)
            response = response.json()

            if response['surveyed_by_owner'] is False:
                surveyed_by_owner = False
                break
    return surveyed_by_owner


class SurveyViewHandler(object):

    @staticmethod
    def generate_survey(request, owner_id: str, vessel_id: str,
                        surveys_path: Path, template):

        # if the owner does not have a subscription
        # then redirect to subscription views
        url = MIR_APP_REST_API + f'owners/{owner_id}'
        response = requests.get(url=url)
        response = response.json()

        if response['subscription_plan_id'] == "None":
            return redirect(to=f'/owner/{owner_id}/not-valid-subscription/')

        # get the available survey types
        url = MIR_APP_REST_API + f'surveys/surveys-types/all'
        survey_type_response = requests.get(url=url)
        survey_type_response = survey_type_response.json()

        if request.method == 'POST':

            data = handle_generate_survey(request,
                                          owner_id=owner_id, vessel_id=vessel_id)

            # get the available survey types
            url = MIR_APP_REST_API + f'vessels/{vessel_id}'
            vessel_type_response = requests.get(url=url)
            vessel_type_response = vessel_type_response.json()

            # create the survey
            url = MIR_APP_REST_API + 'surveys/'

            post_data = {"owner_idx": owner_id,
                         "vessel_idx": vessel_id,
                         "survey_type": survey_type_response[0]['type'],
                         "vessel_type": vessel_type_response["vessel_type"]}

            response = requests.post(url=url, data=json.dumps(post_data))
            response_json = response.json()
            survey_id = response_json['idx']

            try:
                # create the survey directory
                create_survey_directory(directory_path=surveys_path, survey_id=survey_id)
            except ValueError as e:
                print(str(e))

            return redirect(to=f'/owner/{owner_id}/vessel/{vessel_id}/surveys/condition-survey/{survey_id}/')

        context = {'user_auth': True, 'owner_id': owner_id, 'vessel_id': vessel_id,
                   'survey_types': survey_type_response}

        return HttpResponse(template.render(context, request))

    @staticmethod
    def generate_condition_survey_view(request, owner_id: str, vessel_id: str, survey_id: str, template):

        def get_survey_items_wrappers_response(survey_id):

            # get the survey item wrappers
            url_items_wrappers = MIR_APP_REST_API + f'surveys/{survey_id}/items-wrappers'
            survey_items_wrappers_response = requests.get(url=url_items_wrappers)
            survey_items_wrappers_response = survey_items_wrappers_response.json()

            vessel_items_parts = []

            for item_wrapper in survey_items_wrappers_response:
                wrapper_type = item_wrapper['type']
                wrapper_idx = item_wrapper['idx']
                surveyed_by_owner = item_wrapper['surveyed_by_owner']
                vessel_items_parts.append((wrapper_idx, wrapper_type, surveyed_by_owner))

            return vessel_items_parts

        vessel_parts = get_survey_items_wrappers_response(survey_id=survey_id)

        owner_url = MIR_APP_REST_API + f'owners/{owner_id}'
        owner_response = requests.get(url=owner_url)
        owner_response = owner_response.json()

        vessel_url = MIR_APP_REST_API + f'vessels/{vessel_id}'
        vessel_response = requests.get(url=vessel_url)
        vessel_response = vessel_response.json()

        context = {'user_auth': True,
                   'owner_id': owner_id,
                   'vessel_id': vessel_id,
                   'survey_id': survey_id,
                   'owner_name': owner_response['name'],
                   'vessel_name': vessel_response['name'],
                   'vessel_parts': vessel_parts}

        if request.method == 'POST':

            url = MIR_APP_REST_API + f'surveys/{survey_id}/items-wrappers'

            survey_response = requests.get(url=url)
            survey_response = survey_response.json()

            error_message = "A survey can be submitted when all items have been surveyd"
            surveyed_by_owner = all_item_surveyed(response=survey_response)

            if surveyed_by_owner is False:

                context['error_message'] = error_message
                return HttpResponse(template.render(context, request))
            else:
                return SurveyViewHandler.submit_survey(request=request, owner_id=owner_id,
                                                       survey_id=survey_id,
                                                       vessel_id=vessel_id)

        return HttpResponse(template.render(context, request))

    @staticmethod
    def vessel_part_survey_parts_view(request, owner_id: str, survey_id: str, vessel_part_id: str, template):

        url = MIR_APP_REST_API + f'items-wrappers/{vessel_part_id}'
        response = requests.get(url=url)
        response = response.json()

        url = MIR_APP_REST_API + f'surveys/{survey_id}'
        vessel_response = requests.get(url=url)
        vessel_response = vessel_response.json()
        vessel_id = vessel_response['vessel_idx']

        if len(response['survey_parts']) == 0:
            # this is item 5
            return SurveyViewHandler.owner_survey_vessel_part_no_5(request=request, owner_id=owner_id,
                                                                   survey_id=survey_id, vessel_id=vessel_id,
                                                                   vessel_part_id=vessel_part_id)

        vessel_part = response['type']
        vessel_part_code = vessel_part.split(" ")

        # get rid off the first number
        vessel_part_code.pop(0)
        vessel_part_code = "-".join(vessel_part_code)
        vessel_part_code = vessel_part_code.replace("/", "-")
        parts = response['survey_parts']

        wrapper_parts_render = []
        for part in parts:
            url = MIR_APP_REST_API + f'items-wrappers/survey-parts/{part}'

            response = requests.get(url=url)
            response = response.json()

            wrapper_part_type = response['type']
            wrapper_part_idx = response['idx']
            surveyed_by_owner = response['surveyed_by_owner']
            n_images = len(response['images'])

            wrapper_parts_render.append([wrapper_part_idx, wrapper_part_type, surveyed_by_owner, n_images])


        context = {'user_auth': True, 'owner_id': owner_id,
                   'vessel_id': vessel_id,
                   'vessel_part': vessel_part, 'vessel_part_id': vessel_part_id,
                   'vessel_part_code': vessel_part_code,
                   'survey_id': survey_id, 'vessel_parts': wrapper_parts_render}

        print(context['vessel_parts'])

        def check_wrapper_parts(wrapper_parts_render, context):
            for part in wrapper_parts_render:
                if part[2] is False:
                    context['error_message'] = f"Not all parts of {vessel_part} have been surveyd"
                    break
            return context

        if request.method == 'POST':

            if request.POST.get("submitAndContBtn", None) is not None:

                context = check_wrapper_parts(wrapper_parts_render=wrapper_parts_render,
                                              context=context)

                if 'error_message' in context:
                    return HttpResponse(template.render(context, request))

                else:

                    # update the part that it has been surveyed by the owner
                    url = MIR_APP_REST_API + f'items-wrappers/{vessel_part_id}'

                    data = {'surveyed_by_owner': True, 'surveyed_by_surveyor': False,
                            "recommendations": [], "findings": []}
                    
                    response = requests.patch(url=url, data=json.dumps(data))
                    #response = response.json()
                    return redirect(to=f'/owner/{owner_id}/vessel/{vessel_id}/surveys/condition-survey/{survey_id}/')

            elif request.POST.get("submitAndSaveBtn", None) is not None:
                # do work in the back-end and go
                # to the owner surveys
                return redirect(to=f'/owner/{owner_id}/vessel-profile/{vessel_id}/in-progress-surveys/')

        #context = {'user_auth': True, 'owner_id': owner_id,
        #           'vessel_id': vessel_id,
        #           'vessel_part': vessel_part, 'vessel_part_id': vessel_part_id,
        #           'survey_id': survey_id, 'vessel_parts': wrapper_parts_render}

        return HttpResponse(template.render(context, request))

    @staticmethod
    def take_survey_photo_view(request, survey_id: str, owner_id: str,
                               vessel_part: str, survey_part_id: str,
                               surveys_path: Path, max_img_counter: int,
                               template):

        # get the subpart
        #url = MIR_APP_REST_API + f'surveys/survey-part/{survey_part_id}'
        url = MIR_APP_REST_API + f'items-wrappers/survey-parts/{survey_part_id}'

        response = requests.get(url=url)
        response = response.json()

        # get the subpart
        vessel_subpart = response['type']

        survey_url = MIR_APP_REST_API + f'surveys/{survey_id}'
        survey_response = requests.get(url=survey_url)
        survey_response = survey_response.json()
        vessel_id = survey_response['vessel_idx']

        if response['surveyed_by_owner']:
            # we need to show the matrix view
            template_img_preview = loader.get_template(template_ids['image_preview_view'])
            return SurveyViewHandler.vessel_part_subpart_image_preview(request, owner_id=owner_id, survey_id=survey_id,
                                                                       vessel_part=vessel_part,
                                                                       survey_part_id=survey_part_id,
                                                                       max_img_counter=max_img_counter,
                                                                       template=template_img_preview)

        if request.method == 'POST':

            image_path = Path(surveys_path / survey_id / vessel_part / vessel_subpart)
            images = count_number_of_files(filepath=image_path, postfix=['jpg', 'png', 'jpeg'])

            # count how many images do we have
            img_counter = len(images)

            try:
                form_data = handle_uploaded_img(request, survey_id, owner_id,
                                                vessel_id, vessel_part, vessel_subpart)
            except ValueError as e:

                # otherwise we reneder add image view
                context = {'user_auth': True, 'owner_id': owner_id, 'vessel_id': vessel_id,
                           'survey_id': survey_id, 'vessel_part': vessel_part,
                           'vessel_subpart': vessel_subpart, 'survey_part_id': survey_part_id,
                           'img_counter': img_counter + 1, "total_img_counter": max_img_counter,
                           'error_form': 'An image is required'}

                return HttpResponse(template.render(context, request))

            img_filename = form_data['image'].name
            img_filename = vessel_subpart + "_img_" + str(img_counter + 1) + "." + img_filename.split(".")[-1]

            # save the image
            image_path = Path(surveys_path / survey_id / vessel_part / vessel_subpart / img_filename)
            save_image(form_data['image'], filepath=image_path)

            # send the path to the API
            # get the subpart
            url = MIR_APP_REST_API + f'surveys/survey-part/{survey_part_id}/append-img-path'

            data = {'img_path': str(image_path)}
            requests.patch(url=url, data=json.dumps(data))

            # if we reached the maximum nmber of images
            # we go to the preview
            if img_counter + 1 >= max_img_counter:
                return redirect(
                    f'/owner/{owner_id}/surveys/condition-survey/{survey_id}/{vessel_part}/{survey_part_id}/image-preview/')
            else:

                # otherwise we reneder add image view
                context = {'user_auth': True, 'owner_id': owner_id, 'vessel_id': vessel_id,
                           'survey_id': survey_id, 'vessel_part': vessel_part,
                           'vessel_subpart': vessel_subpart, 'survey_part_id': survey_part_id,
                           'img_counter': img_counter + 1, "total_img_counter": max_img_counter}

                return HttpResponse(template.render(context, request))
        else:

            try:
                # save the image to the surveys
                create_survey_directory(directory_path=surveys_path / survey_id, survey_id=vessel_part)
            except ValueError as e:
                print(f"WARNING: {str(e)}")

            try:
                create_survey_directory(directory_path=surveys_path / survey_id / vessel_part, survey_id=vessel_subpart)
            except ValueError as e:
                print(f"WARNING: {str(e)}")

            image_path = surveys_path / survey_id / vessel_part / vessel_subpart
            images = count_number_of_files(filepath=image_path, postfix=['jpg', 'png', 'jpeg'])

            context = {'user_auth': True, 'owner_id': owner_id, 'vessel_id': vessel_id,
                       'survey_id': survey_id, 'vessel_part': vessel_part,
                       'vessel_subpart': vessel_subpart, 'survey_part_id': survey_part_id,
                       'img_counter': len(images), "total_img_counter": max_img_counter}

            return HttpResponse(template.render(context, request))

    @staticmethod
    def submit_vessel_subpart_images(request, survey_id: str, owner_id: str,
                                     vessel_id: str, vessel_part_id: str, survey_part_id: str):

        url = MIR_APP_REST_API + f'surveys/survey-part/{survey_part_id}/submit-images'
        data = {"surveyed_by_owner": True}
        requests.patch(url=url, data=json.dumps(data))
        return redirect(to=f'/owner/{owner_id}/surveys/condition-survey/{survey_id}/{vessel_part_id}/vessel-part-survey-parts/')

    @staticmethod
    def vessel_part_subpart_image_preview(request, survey_id: str, owner_id: str,
                                          vessel_part: str, survey_part_id: str,
                                          max_img_counter: int,
                                          template):

        # get the subpart
        url = MIR_APP_REST_API + f'items-wrappers/survey-parts/{survey_part_id}'
        #f'surveys/survey-part/{survey_part_id}'

        response = requests.get(url=url)
        response = response.json()

        vessel_part_id = response['survey_item_wrapper_idx']

        survey_url = MIR_APP_REST_API + f'surveys/{survey_id}'
        survey_response = requests.get(url=survey_url)
        survey_response = survey_response.json()
        vessel_id = survey_response['vessel_idx']

        def get_images(from_response):
            images = []
            for img in from_response['images']:
                img = str(img)
                img_details = img.split("/")
                img = survey_id + "/" + vessel_part + "/" + from_response['type'] + "/" + img_details[-1]

                img_id = img_details[-1]
                images.append((img, img_details[-1], img_id))
            return images

        images = get_images(from_response=response)

        context = {'user_auth': True, 'owner_id': owner_id, 'vessel_id': vessel_id,
                   'survey_id': survey_id, 'vessel_part': vessel_part,
                   'vessel_subpart': response['type'], 'survey_part_id': survey_part_id,
                   'img_counter': len(images), "total_img_counter": max_img_counter,
                   'images': images, 'media_url': MEDIA_URL}

        if len(images) < max_img_counter:
            context["add_more_photos_btn"] = True

        if request.method == 'POST':

            if len(response['images']) < max_img_counter:
                if len(response['images']) >= MIN_NUM_IMG:
                    return SurveyViewHandler.submit_vessel_subpart_images(request, survey_id=survey_id,
                                                                          owner_id=owner_id,
                                                                          vessel_id=vessel_id,
                                                                          vessel_part_id=vessel_part_id,
                                                                          survey_part_id=survey_part_id)
                else:
                    context["error_message"] = f"You need to add at least {MIN_NUM_IMG} photos"
                    return HttpResponse(template.render(context, request))
            else:
                return SurveyViewHandler.submit_vessel_subpart_images(request, survey_id=survey_id, owner_id=owner_id,
                                                                      vessel_id=vessel_id,
                                                                      vessel_part_id=vessel_part_id,
                                                                      survey_part_id=survey_part_id)

        return HttpResponse(template.render(context, request))

    @staticmethod
    def view_photo(request, owner_id: str, survey_id: str, vessel_part: str,
                   survey_part_id: str, image_id: str, template):

        # get the subpart
        url = MIR_APP_REST_API + f'items-wrappers/survey-parts/{survey_part_id}'
        #f'surveys/survey-part/{survey_part_id}'

        response = requests.get(url=url)
        response = response.json()
        context = {'media_url': MEDIA_URL, 'owner_id': owner_id, 'survey_id': survey_id,
                   'img_id': survey_id + "/" + vessel_part + "/" + response['type']  + "/" + image_id,
                   'vessel_part': vessel_part, 'vessel_subpart': response['type'],
                   'survey_part_id': survey_part_id}
        return HttpResponse(template.render(context, request))

    @staticmethod
    def submit_survey(request, owner_id: str, vessel_id: str, survey_id: str):

        # we need to let the back-end that the survey
        # a survey can be submitted when all survey item wrappers
        # have been submitted

        # find the owner via email
        url = MIR_APP_REST_API + f'surveys/{survey_id}/submit'
        response = requests.patch(url=url)
        return redirect(f'/owner/{owner_id}/vessel-profile/{vessel_id}/in-progress-surveys/')

    @staticmethod
    def delete_survey_from_vessel(request, owner_id: str, vessel_id: str, survey_id: str, template):

        if request.method == 'POST':

            # find the owner via email
            url = MIR_APP_REST_API + f'surveys/{survey_id}/'
            response = requests.delete(url=url)
            return redirect(f'/owner/{owner_id}/vessel-profile/{vessel_id}/in-progress-surveys/')
        else:

            context = {'owner_id': owner_id, 'vessel_id': vessel_id, 'survey_id': survey_id}
            return HttpResponse(template.render(context, request))

    @staticmethod
    def survey_part_summary_view(request, survey_id, vessel_part, template):
        context = {'vessel_part': vessel_part}
        return HttpResponse(template.render(context, request))

    @staticmethod
    def view_owner_survey_request_summary(request, owner_id: str, vessel_id, survey_id: str, template):

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

    @staticmethod
    def vessel_surveys_in_progress_view(request, owner_id: str, vessel_id: str, template):

        vessel_url = MIR_APP_REST_API + f"vessels/{vessel_id}"

        response = requests.get(url=vessel_url)
        response_json = response.json()
        vessel_name = response_json['name']

        # get the surveys that are in progress
        # for this vessel and this owner
        url = MIR_APP_REST_API + f"surveys/?vessel_id={vessel_id}"
        response = requests.get(url=url)
        response_json = response.json()

        in_progress_surveys = []
        pending_surveys = []
        completed_surveys_reqs = []
        in_progress_surveyor = []
        for survey in response_json:

            survey_type = survey['survey_type']
            survey_idx = survey['idx']
            survey_result_url = MIR_APP_REST_API + f'surveys/{survey_idx}/survey-result'
            survey_result_doc = requests.get(url=survey_result_url)
            survey_result_response_json = survey_result_doc.json()

            print(survey_result_response_json)
            if survey_result_response_json['owner_survey_status'] == 'IN_PROGRESS':
                in_progress_surveys.append((survey['idx'], survey_type,
                                            survey['created_at'].split(" ")[0], 'IN_PROGRESS'))

            elif survey_result_response_json['owner_survey_status'] == 'COMPLETED' and \
                    survey_result_response_json['survey_request_status'] == 'PENDING':
                pending_surveys.append((survey['idx'], survey_type,
                                        survey['created_at'].split(" ")[0],
                                        survey_result_response_json['survey_request_status']))
            elif survey_result_response_json['owner_survey_status'] == 'COMPLETED' and \
                    survey_result_response_json['survey_request_status'] == 'COMPLETED':

                completed_surveys_reqs.append((survey['idx'], survey_type,
                                               survey['created_at'].split(" ")[0], 
                                               survey_result_response_json['survey_request_status']))
            elif survey_result_response_json['owner_survey_status'] == 'COMPLETED' and \
                    survey_result_response_json['survey_request_status'] == 'IN_PROGRESS':
                in_progress_surveyor.append((survey['idx'], survey_type,
                                               survey['created_at'].split(" ")[0],
                                               'SURVEYOR_IN_PROGRESS'))

        context = {'user_auth': True, 'owner_id': owner_id,
                   'vessel_id': vessel_id,
                   'in_progress_surveys': in_progress_surveys,
                   'pending_surveys_reqs': pending_surveys,
                   'completed_surveys_reqs': completed_surveys_reqs,
                   'in_progress_surveyor': in_progress_surveyor,
                   'vessel_name': vessel_name}

        #if len(pending_surveys) == 0 and len(completed_surveys_reqs) == 0:
        #context['no_surveys'] = True

        return HttpResponse(template.render(context, request))

    @staticmethod
    def download_survey(request, owner_id: str,
                         survey_id: str, filename='survey.pdf') -> HttpResponse:

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
        #mime_type, _ = mimetypes.guess_type(filename)

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

    @staticmethod
    def owner_survey_vessel_part_no_5(request, owner_id: str,
                                      survey_id: str, vessel_id: str,
                                      vessel_part_id: str):

        if request.method == 'POST':
            # collect the data and redirect
            # make the updates and mark the section as
            # finished
            return redirect(to=f'/owner/{owner_id}/vessel/{vessel_id}/surveys/condition-survey/{survey_id}/')

        print("I am heer")
        template = loader.get_template(template_ids['owner_survey_vessel_part_no_5'])
        context = {'condition_types': ["Collisions", "Grounding", "Lightning/Electrical surge", "Broaching/crash-gybe", "Flooding/swamping",
                                       "Structural conversions", "None"],
                   'owner_id':owner_id, 'survey_id': survey_id,
                   'vessel_id': vessel_id, 'vessel_part_id': vessel_part_id}

        return HttpResponse(template.render(context, request))

