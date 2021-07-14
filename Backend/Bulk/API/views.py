from django.shortcuts import render
from django.http import HttpResponse, response
from django.views.decorators.csrf import csrf_exempt


import json
import requests

def apiGetToken(clientId,clientSecret,siteUrl):
    #API Call
    #Get token from client_id and Secret
    request_payload = {
        'grant_type': 'client_credentials',
        'client_id': clientId,
        'client_secret': clientSecret
    }
    request_url = f'https://{siteUrl}/api/access/v1/oauth/token'
    OneTrustResponse = requests.post(request_url, params=request_payload)
    OneTrustResponseJSON = OneTrustResponse.json()
    if 'error' in OneTrustResponseJSON:
        print('Get Token Error | '+OneTrustResponseJSON['error'] +' | ' +OneTrustResponseJSON['error_description']) #Print Error Message
    access_token = OneTrustResponseJSON['access_token']
    return(access_token)

def apiGetPurposeList(accessToken,siteUrl):
    #API Call
    #Get Purpose List from OneTrust
    headers = {
        'Authorization': f'Bearer {accessToken}'
    }
    request_payload = {
        'size':'200', #Default was 20 which is not enough
        'latestVersion': 'true' #Not sure if this needed
    }
    request_url = f'https://{siteUrl}/api/consentmanager/v2/purposes/'
    respond = requests.get(request_url, headers=headers, params=request_payload)
    respond_json = respond.json()
    purpose_list = respond_json
    return purpose_list

def parsePurposeJSON(purposeCSV):
    parsedPurpose = []
    for item in purposeCSV:
        parsedPurpose.append(
        {
            "Name": item["Name"],
            "DefaultLanguage": item['DefaultLanguage'],
            "Description": item['Description'],
            "ConsentLifeSpan": item['ConsentLifeSpan'],
            "Organizations": [
                item['Organizations']
            ], #API Require this field as list
            "Languages":[
                {
                    'Language': item['Language1'],
                    'Name': item['NameLanguage1'],
                    'Default': item['DefaultLanguage1'].lower(),
                    'Description': item['DescriptionLanguage1']
                },
                {
                    'Language': item['Language2'],
                    'Name': item['NameLanguage2'],
                    'Default': item['DefaultLanguage2'].lower(),
                    'Description': item['DescriptionLanguage2']
                }
            ]
        }
    )
    return(parsedPurpose)

def apiCreateConsentPurpose(accessToken,siteUrl,parsedPurpose):
    #API Call
    #Create purpose from parsed CSV file
    createConsentPurposeResult = []
    createConsentPurposeResultLog = []
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {accessToken}'
    }
    request_url = f'https://{siteUrl}/api/consentmanager/v1/purposes'
    for item in parsedPurpose:
        request_payload = item
        respond = requests.post(request_url, headers=headers, data=json.dumps(request_payload))
        respond_json = respond.json()
        createConsentPurposeResultLog.append(respond_json)
    print('Purpose Created Result')
    for item in createConsentPurposeResultLog:
        if 'message' in item:
            print('Error! | '+item['message']) #Print Error Message
            createConsentPurposeResult.append(
                {
                    "CreateStatus" : "Error",
                    "ErrorMessage" : item['message']
                }
            )
        else:
            print('Created! | Purpose Name : '+item['Label']+ ' |' + ' ID : '+item['Id']+ ' |' ' Status : '+item['Status']) #Print Success Message + Items
            createConsentPurposeResult.append(
                {
                    "CreateStatus" : "Success",
                    "PurposeName" : item['Label'],
                    "PurposeId" : item['Id'],
                    "Status" : item['Status']
                }
            )
    return createConsentPurposeResult


def updatePurposeList(accessToken,siteUrl,parsedPurpose):
    # Get recently created consent id from API and Update to the purpose
    purposeList = apiGetPurposeList(accessToken,siteUrl) #Get OT Purpose List from API
    for purpose in parsedPurpose:
        for content in purposeList['content']:
            if purpose['Name'] in content['versions'][0]['label']: #Match Purpose ID of recently created purpose to existing data
                purpose['purposeId'] = content['purposeId']
                purpose['Label'] = content['versions'][0]['label']
                purpose['Version'] = content['versions'][0]['version']
                purpose['Status'] = content['versions'][0]['status']
    return parsedPurpose

def apiUpdateConsentPurpose(accessToken,siteUrl,parsedPurpose):
    # Update recently created purpose with API from Updated CSV (with ID)
    updateConsentPurposeResult = []
    updateConsentPurposeResultLog = []
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {accessToken}'
    }
    for items in parsedPurpose:
        purposeId = items['purposeId']
        request_url = f'https://{siteUrl}/api/consentmanager/v1/purposes/{purposeId}'
        request_payload = items
        respond = requests.put(request_url, headers=headers, data=json.dumps(request_payload)) #Data have to be sent in JSON format
        respond_json = respond.json()
        updateConsentPurposeResultLog.append(respond_json)
        print(respond_json)
        print(updateConsentPurposeResultLog)
    print('Purpose Update Result')
    for item in updateConsentPurposeResultLog:
        if 'message' in item:
            print('Error! | '+item['message']) #Print Error Message
            updateConsentPurposeResult.append(
                {
                    "UpdateStatus" : "Error",
                    "ErrorMessage" : item['message']
                }
            )
        else:
            print('Updated! | Purpose Name : '+item['Label']+ ' |' + ' ID : '+item['Id']+ ' |' ' Status : '+item['Status']) #Print Success Message + Items
            updateConsentPurposeResult.append(
                {
                    "UpdateStatus" : "Success",
                    "PurposeName" : item['Label'],
                    "PurposeId" : item['Id'],
                    "Status" : item['Status']
                }
            )
    return updateConsentPurposeResult

# Create your views here.
@csrf_exempt
def makeRequest(request):
    if request.method == 'POST':
        try:
            payload = json.loads(request.body)
            clientId = payload['clientId']
            clientSecret = payload['clientSecret']
            siteUrl = payload['siteUrl']
            purposeCSV = payload['purposeCSV']
            accessToken = apiGetToken(clientId,clientSecret,siteUrl)
            parsedPurpose = parsePurposeJSON(purposeCSV)
            createdResult = apiCreateConsentPurpose(accessToken,siteUrl,parsedPurpose)
            updatedPurpose = updatePurposeList(accessToken,siteUrl,parsedPurpose)
            updatedResult = apiUpdateConsentPurpose(accessToken,siteUrl,parsedPurpose)
            #print(updateResult)

            response = json.dumps(
            [
                {
                    "Status": "OK",
                    "AccessToken": accessToken,
                    "CreateResult": createdResult,
                    "UpdateResult" : updatedResult,
                    "UpdatedPurpose": updatedPurpose,
                }
            ])
        except:
            response = json.dumps([{
                    'Status' : "Error",
                    'Error_Message' : "Wrong API structure"
                }])

        return HttpResponse(response,content_type='application/json')
