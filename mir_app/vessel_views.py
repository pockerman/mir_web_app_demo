import json
import requests
from pathlib import Path
from django.shortcuts import redirect
from django.http import HttpResponse

from mir_app.form_handlers import handle_vessel_registration
from mir_app.config import MIR_APP_REST_API


class VesselViewsHandler(object):

    @staticmethod
    def vessel_profile(request, owner_id: str, vessel_id: str, template):

        url = MIR_APP_REST_API + f'vessels/{vessel_id}/?mmsi=false&ce=false'

        # retrieve the vessel data
        response = requests.get(url=url, data=json.dumps({}))
        response_json = response.json()

        context = {'user_auth': True,
                   'owner_id': owner_id, 'vessel_id': vessel_id}
        context.update(response_json)
        context['vessel_name'] = context['name']
        return HttpResponse(template.render(context, request))

    @staticmethod
    def vessel_registration(request, owner_id: str, template):

        if request.method == 'POST':
            response = handle_vessel_registration(request, owner_id)

            # register the vessel
            response_json = response.json()
            return redirect(f'/owner/{owner_id}/vessel-profile/{response_json["idx"]}')
        else:
            # get the vessel types

            url = MIR_APP_REST_API + f'vessels/types'
            response = requests.get(url=url)
            response_json = response.json()

            context = {'user_auth': True, 'owner_id': owner_id,
                       'vessel_types': response_json,
                       'construction_types': ["Wood",  "GRP", "Carbon", "Aluminium", "Steel", "Other"],
                       'propulsion_types': ['Motor', 'Sail']}
            return HttpResponse(template.render(context, request))


