import datetime
from django.contrib import messages
from django.shortcuts import render,redirect,HttpResponseRedirect
from requests import Response
from mainapp.views import *
import json
from .forms import *
from .decorator import *
from mainapp.views import get_service_plan
from django.conf import settings
from django.http import HttpResponse
ENDPOINT = 'api/'

def format_data(MSID,data):
    response = {
        'ms_id':MSID,
        'ms_payload':json.dumps(data)
    }
    json_response = json.dumps(response)
    return json_response

def call_post_method_with_token(URL,endpoint,data,access_token, files=None):
    api_url = URL + endpoint
    headers = { "Authorization":f'Bearer {access_token}'}
    if files:
        print("inide_the_files")
        response = requests.post(api_url,data=data, files=files, headers=headers)
    else:
        
        headers["Content-Type"] = "application/json"

        response = requests.post(api_url,data=data,headers=headers)
        print("response567890",response)
    return response

@custom_login_required
def customer_workspace(request):
        # try:
                token=request.session['user_token']
                document_entity_MSID = get_service_plan('entity master view')
                document_entity_data = format_data(document_entity_MSID,{})
                print("document_entity_data99",document_entity_data)
                document_entity_response = call_post_method_with_token_v2(BASEURL,ENDPOINT,document_entity_data,token)
                print("document_entity_response",document_entity_response)
              
                if document_entity_response['status_code'] != 0:
                        print('document_entity_response error',document_entity_response)
                document_entity_list = document_entity_response['data']
                print("document_entity_list===8979",document_entity_list)
               
               
                context={
                        "matter_workspace":'active',
                        'document_entity_list':document_entity_list,
                }
                return render (request,'DMS/customer_workspace.html',context)
        # except Exception as error:
        #         return render(request, "error.html", {"error": error})


@custom_login_required
def document_storage(request,entity_id):
#     try:
        token = request.session['user_token']
        #folder gettiing
        folder_MSID = get_service_plan('entity folders list')
        data = format_data(folder_MSID,{'entity_id':entity_id})
        folder_list_response = call_post_method_with_token(BASEURL,ENDPOINT,data,token)
        print('folder-list=========',folder_list_response)
        if folder_list_response.status_code == 200:
                print('folder_list_response',folder_list_response)
                folder_list = folder_list_response.json()
                print("folder_list9876543",folder_list)
                for item in folder_list:
                        print("item34567899oihgbvhnjk", item)
                        # Convert 'created_at' field
                        item['created_at'] = datetime.datetime.strptime(item['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d')
                        print('item_date', item)

                        # Convert 'update_at' field
                        item['update_at'] = datetime.datetime.strptime(item['update_at'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d')
                        print('item_date', item)
                else:
                        # return JsonResponse({'error': 'Failed to save form data'}, status=400)
                        messages.info(request, "Oops..! Application Failed to Submitted..")
                        print('folder_list',folder_list_response)


        # mistake is folder_list
        # form=CreatEventForm()
        folder_form = FolderForm()

        #'client_id_list':client_id_list,'matter_id_list':matter_id_list
        context={
                # "form":form,
                'folder_form':folder_form,
                'folder_list':folder_list,
                'main_folder':True,
                'entity_id':entity_id,
                # 'client_view':client_view,
                # 'matter_view':matter_view,
                "document_stor_active":"active"
        }
        return render(request, 'DMS/document_storage.html',context)
#     except Exception as error:
#         return render(request, "error.html", {"error": error})    



@custom_login_required
def folder(request,entity_id,folder_id):
#     try:     
        token = request.session['user_token']

        # folder gettiing
        MSID = get_service_plan('folder master view')
        print('MSID--',MSID)
        value={
                'folder_id':folder_id
        }
        data = format_data(MSID,value)
        print('data',data)
        folder_list_response = call_post_method_with_token(BASEURL,ENDPOINT,data,token)
        if folder_list_response.status_code != 200:
                print('folder_list_response error',folder_list_response)
                print('folder_list_response error',folder_list_response.json())
        folder_list = folder_list_response.json()
        print('folder_list888888',folder_list)
        for item in folder_list:
                print("item34567899oihgbvhnjk55555", item)
                # Convert 'created_at' field
                item['created_at'] = datetime.datetime.strptime(item['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d')
                print('item_date', item)

                # Convert 'update_at' field
                item['update_at'] = datetime.datetime.strptime(item['update_at'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d')
        # document list

        document_MSID = get_service_plan('folder documents list')
        document_data = format_data(document_MSID,{'folder_id':folder_id})
        print('document_type_responsedocument_data===',type(document_data))

        document_response = call_post_method_with_token(BASEURL,ENDPOINT,document_data,token)
        if document_response.status_code != 200:
                print('document_response error',document_response)
        document_list = document_response.json()
        print('document_list',document_list)
        for item in document_list:
                        item['update_at'] = datetime.datetime.strptime(item['update_at'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d') 
                        # start_date = datetime.strptime(item['start_date'], '%Y-%m-%d')
                        # end_date = datetime.strptime(item['end_date'], '%Y-%m-%d')
                        # # Calculate the remaining days
                        # remaining_days = (end_date - start_date).days
                        # # Assign the remaining days to the item
                        # item['remaining_days'] = remaining_days
                        # print('item_date',item)
         
        #  document_category
        document_cat_MSID = get_service_plan('document category view')
        data = format_data(document_cat_MSID,{})
        document_cat_response = call_post_method_with_token(BASEURL,ENDPOINT,data,token)
        if document_cat_response.status_code != 200:
                print('document_cat_response error',document_cat_response)
        document_cat_list = document_cat_response.json()

        #  document type
        document_type_MSID = get_service_plan('document type view')
        data = format_data(document_type_MSID,{})
        document_type_response = call_post_method_with_token(BASEURL,ENDPOINT,data,token)
        if document_type_response.status_code != 200:
                print('document_type_response error',document_type_response)
        document_type_list = document_type_response.json()

        # document entity
        document_entity_MSID = get_service_plan('entity master view')
        document_entity_data = format_data(document_entity_MSID,{})
        document_entity_response = call_post_method_with_token(BASEURL,ENDPOINT,document_entity_data,token)
        if document_entity_response.status_code != 200:
                print('document_entity_response error',document_entity_response)
        document_entity_list = document_entity_response.json()
        

        

        folder_form = FolderForm()
        document_form = DocumentUploadForm()
        context={
                "BASEURL":BASEURL,
                'folder_form':folder_form,
                'folder_list':folder_list,
                'entity_id':entity_id,
                "matter_workspace":"active",
                'folder_id':folder_id,
                'document_type_list':document_type_list,
                'document_cat_list':document_cat_list,
                'document_entity_list':document_entity_list,
                'document_form':document_form,
                'document_list':document_list,
        }
        return render(request, 'DMS/document_storage.html',context)
#     except Exception as error:
#                 return render(request, "error.html", {"error": error})
