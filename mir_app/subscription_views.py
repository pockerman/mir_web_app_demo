import json
import requests
from pathlib import Path
from django.shortcuts import redirect
from django.http import HttpResponse

from mir_app.config import MIR_APP_REST_API



class SubscriptionsViewHandler(object):

    @staticmethod
    def not_valid_subscription_view(request, owner_id: str, template):
        context = {'user_auth': True, 'owner_id': owner_id}
        return HttpResponse(template.render(context, request))

    @staticmethod
    def buy_subscription_view(request, owner_id: str, subscription_type: str, template):

        if request.method == 'POST':
            print("Method is post")

            # update the subscription flag for the owner
            url = MIR_APP_REST_API + f'subscrpitions/{owner_id}/update'
            data = {'subscription_plan_id':'123'}
            response = requests.post(url=url, data=json.dumps(data))
            return redirect(to=f'/owner/{owner_id}/dashboard/')

        context = {'user_auth': True, 'owner_id': owner_id,
                   'subscription_type': subscription_type}

        return HttpResponse(template.render(context, request))
