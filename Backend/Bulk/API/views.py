from django.shortcuts import render
from django.http import HttpResponse, response
from django.views.decorators.csrf import csrf_exempt


import json
import requests

# Create your views here.
@csrf_exempt
def getToken(request):
    if request.method == 'POST':
        try:
            payload = json.loads(request.body)
            clientId = payload['clientId']
            clientSecret = payload['clientSecret']
            siteUrl = payload['siteUrl']
            request_payload = {
            'grant_type': 'client_credentials',
            'client_id': clientId,
            'client_secret': clientSecret
            }
            request_url = f'https://{siteUrl}/api/access/v1/oauth/token'
            response = requests.post(request_url, params=request_payload)
        except:
            response = json.dumps([{
                'error' : 'try/except return error'
            }])

        return HttpResponse(response,content_type='application/json')
