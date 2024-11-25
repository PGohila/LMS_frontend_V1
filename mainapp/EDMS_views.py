import base64
import datetime
import random
import string
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

def generate_random_id(pre):
    suffix = ''.join(random.choices(string.digits, k=5))  # Generate a 6-digit random suffix
    return pre + suffix

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
        company_id = request.session.get('company_id')
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
        # document_type_MSID = get_service_plan('document type view')
        # data = format_data(document_type_MSID,{})
        # document_type_response = call_post_method_with_token(BASEURL,ENDPOINT,data,token)
        # if document_type_response.status_code != 200:
        #         print('document_type_response error',document_type_response)
        # document_type_list = document_type_response.json()

        MSID = get_service_plan('view identificationtype') # view_identificationtype
        if MSID is None:
            print('MSID not found')
        data = {'ms_id': MSID,'ms_payload': {'company_id':company_id}}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        document_type_list= response['data']
        print("document_type_list4567890",document_type_list)

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


@custom_login_required
def create_folder(request,entity_id):
     try: 
        company_id = request.session.get('company_id')    
        if request.method == 'POST':
                token = request.session['user_token']
                form = FolderForm(request.POST)
                if form.is_valid():
                        MSID = get_service_plan('folder master create')
                        cleaned_data = form.cleaned_data
                        cleaned_data['entity_id']=entity_id
                        cleaned_data['default_folder']=True   #changes made
                        document_create_name=cleaned_data['folder_name']
                        print("document_create_name",document_create_name)
                        data = format_data(MSID,cleaned_data)
                        folder_list_response = call_post_method_with_token(BASEURL,ENDPOINT,data,token)
#========================================================
                        # matter_create = response['data']
                        # data1 = matter_create[0]
                        # print('data---', data1)
#============================================================                        
                        if folder_list_response.status_code != 200:
                                print('folder_list_response error',folder_list_response)
                        else:
                                print(folder_list_response.json())
                        return redirect(f'/document_storage/{entity_id}/')
                else:
                        print(form.errors)
        else:
                messages.info(request, "Oops..! Application Failed to Submitted..")
     except Exception as error:
                return render(request, "error.html", {"error": error})
                




@custom_login_required
def create_sub_folder(request,entity_id,folder_id):
     try:
        if request.method == 'POST':
                token = request.session['user_token']
                form = FolderForm(request.POST)
                if form.is_valid():
                        MSID = get_service_plan('folder master create')
                        cleaned_data = form.cleaned_data
                        cleaned_data['parent_folder_id']=folder_id
                        cleaned_data['entity_id']=entity_id
                        data = format_data(MSID,cleaned_data)
                        print('data',data)
                        folder_list_response = call_post_method_with_token(BASEURL,ENDPOINT,data,token)
                        if folder_list_response.status_code != 200:
                                print('folder_list_response error',folder_list_response)
                        else:
                                print(folder_list_response.json())
                                return HttpResponseRedirect(f'/folder/{entity_id}/{folder_id}/')
                
                else:
                        print('f==',form.errors)
        else:
                messages.info(request, "Oops..! Application Failed to Submitted..")
     except Exception as error:
                return render(request, "error.html", {"error": error})


@custom_login_required
def upload_document(request,entity_id,folder_id):
        try:
                company_id = request.session.get('company_id')
                print('entity_1234567id===',entity_id)
                print('folder_id',folder_id)
                if request.method == 'POST':
                        token = request.session['user_token']
                        print('request123',request)
                        print('request.POST',request.POST)
                        print('request.POST',request.FILES)
                        form = DocumentUploadForm(request.POST,request.FILES)
                        if form.is_valid():
                                # document upload
                                MSID = get_service_plan('document upload')
                                cleaned_data = form.cleaned_data
                                print(",,,,,,,,,,,,,",cleaned_data)
                                cleaned_data['folder_id']=folder_id
                                cleaned_data['company_id']=company_id
                                cleaned_data['entity_type']=[entity_id]
                                if cleaned_data['start_date'] is not None:
                                        cleaned_data['start_date'] = cleaned_data['start_date'].strftime('%Y-%m-%d')
                                else:
                                        cleaned_data['start_date'] = None

                                if cleaned_data['end_date'] is not None:
                                        cleaned_data['end_date'] = cleaned_data['end_date'].strftime('%Y-%m-%d')
                                else:
                                        cleaned_data['end_date'] = None  
                                document_upload_name=cleaned_data['document_title']
                                print("document_upload_name",document_upload_name)

                                document_upload = request.FILES['document_upload']
                                print("document_upload7890",document_upload)
                                document_upload_filename = document_upload.name
                                # cleaned_data['document_upload'] = document_upload_filename
                                del cleaned_data['document_upload']
                                files = {'files': (document_upload.name, document_upload.read())}
                                
                                data = format_data(MSID,cleaned_data)
                                print('data///',data)
                                response = {
                                        'ms_id':MSID,
                                        'ms_payload':json.dumps(cleaned_data)
                                }
                                data= json.dumps(response)
                                print("data00",data)
                                # upload_document_name=data['ms_payload']['document_title']
                                # print('upload_document_name',upload_document_name)
                                response = call_post_method_with_token(BASEURL,ENDPOINT,response, token,files)
                                print('response======reee',response)
#========================================================
#============================================================
                                if response.status_code != 200:
                                        print('response error',response)
                                else:
                                        print(response.json())
                                        messages.info(request, "Upload Successfully")
                                        return redirect(f'/folder/{entity_id}/{folder_id}/')
                        else:
                                print(form.errors)
                else:
                        messages.info(request, "Oops..! Application Failed to Submitted..")
        except Exception as error:
                return render(request, "error.html", {"error": error})



@custom_login_required
def document_category(request):
        try:
                token=request.session['user_token']
                # document category view
                document_cat_MSID = get_service_plan('document category view')
                document_cat_data = format_data(document_cat_MSID,{})
                document_cat_response = call_post_method_with_token(BASEURL,ENDPOINT,document_cat_data,token)
                if document_cat_response.status_code != 200:
                        print('document_cat_response error',document_cat_response)
                document_cat_records = document_cat_response.json()
                # department view
                department_MSID = get_service_plan('department view')
                department_data = format_data(department_MSID,{})
                department_response = call_post_method_with_token(BASEURL,ENDPOINT,department_data,token)
                if department_response.status_code != 200:
                        print('department_response error',department_response)
                department_records = department_response.json()
                print('department_records',department_records)

                form = DocumentCategoryForm()
                if request.method=='POST':
                        form=DocumentCategoryForm(request.POST)
                        if form.is_valid():
                                # document category create
                                MSID = get_service_plan('document category create')
                                cleaned_data = form.cleaned_data
                                data = format_data(MSID,cleaned_data)
                                folder_list_response = call_post_method_with_token(BASEURL,ENDPOINT,data,token)
                                if folder_list_response.status_code != 200:
                                        print('folder_list_response error',folder_list_response)
                                else:
                                        print(folder_list_response.json())
                                        return HttpResponseRedirect(f'/document_category/')
                        else:
                                print(form.errors)
                
                context={
                                'form':form,'document_cat_records':document_cat_records,'department_records':department_records
                }
                return render (request,'DMS/document_category.html',context)
        
        except Exception as error:
                return render(request, "error.html", {"error": error})


@custom_login_required
def department(request):
        try:
                token=request.session['user_token']
                # department view
                department_MSID = get_service_plan('department view')
                print('department_MSID',department_MSID)
                department_data = format_data(department_MSID,{})
                department_response = call_post_method_with_token(BASEURL,ENDPOINT,department_data,token)
                if department_response.status_code != 200:
                        print('department_response error',department_response)
                department_records = department_response.json()

                form = DepartmentForm()
                if request.method=='POST':
                        form=DepartmentForm(request.POST)
                        if form.is_valid():
                                # department create
                                MSID = get_service_plan('department create')
                                cleaned_data = form.cleaned_data
                                data = format_data(MSID,cleaned_data)
                                folder_list_response = call_post_method_with_token(BASEURL,ENDPOINT,data,token)
                                if folder_list_response.status_code != 200:
                                        print('folder_list_response error',folder_list_response)
                                else:
                                        print(folder_list_response.json())
                                        return HttpResponseRedirect(f'/department/')
                        else:
                                print(form.errors)
                                
                context={
                        'form':form,'department_records':department_records
                }
                return render (request,'DMS/department.html',context)
        except Exception as error:
                return render(request, "error.html", {"error": error})


@custom_login_required
def document_type(request):
        try:
                token=request.session['user_token']
                # document type view
                document_type_MSID = get_service_plan('document type view')
                document_type_data = format_data(document_type_MSID,{})
                document_type_response = call_post_method_with_token(BASEURL,ENDPOINT,document_type_data,token)
                if document_type_response.status_code != 200:
                        print('document_type_response error',document_type_response)
                document_type_records = document_type_response.json()

                form = DocumentTypeForm()
                if request.method=='POST':
                        form=DocumentTypeForm(request.POST)
                        if form.is_valid():
                                # document type create
                                MSID = get_service_plan('document type create')
                                cleaned_data = form.cleaned_data
                                data = format_data(MSID,cleaned_data)
                                print("data56789098765",data)
                                response = call_post_method_with_token(BASEURL,ENDPOINT,data,token)
                                if response.status_code != 200:
                                        print('response error',response)
                                else:
                                        print("document_type98765432345678",response.json())
                                        messages.info(request, "Created Successfully")
                                        return HttpResponseRedirect(f'/document_type/')
                        else:
                                print(form.errors)
                # else:
                #        messages.info(request, "Oops..! Application Failed to Submitted..")
                    
                context={
                        'form':form,'document_type_records':document_type_records
                }
                return render (request,'DMS/document_type.html',context)
        
        except Exception as error:
                return render(request, "error.html", {"error": error})



@custom_login_required
def document_entity(request):

        token=request.session['user_token']
        user_name = request.session['username']
        user_role=request.session['user_role']
        user_profile=request.session['user_profile']
        notification =request.session['notification']
        # entity master view
        document_entity_MSID = get_service_plan('entity master view')
        print('document_entity_MSID',document_entity_MSID)
        document_entity_data = format_data(document_entity_MSID,{})
        document_entity_response = call_post_method_with_token(BASEURL,ENDPOINT,document_entity_data,token)
        if document_entity_response.status_code != 200:
                print('document_entity_response error',document_entity_response)
        document_entity_records = document_entity_response.json()

        form = DocumentEntityForm()
        if request.method=='POST':
                form=DocumentEntityForm(request.POST)
                print("formss",form)
                if form.is_valid():
                    # entity master create
                        MSID = get_service_plan('entity master create')
                        cleaned_data = form.cleaned_data
                        cleaned_data['entity_id']=generate_random_id('EID')
                        document_entity_name=cleaned_data['entity_name']
                        print("document_entity_name",document_entity_name)
                        data = format_data(MSID,cleaned_data)

                        response = call_post_method_with_token(BASEURL,ENDPOINT,data,token)
#========================================================
#============================================================
                        
                        if response.status_code != 200:
                                #     if "document_entity_add" in notification:
                                messages.info(request,"Successfully Created")
                                print('response error',response)
                        else:
                                print(response.json())
                                messages.info(request, "Successfully Created")
                                return HttpResponseRedirect(f'/document_entity/')
                else:
                      print(form.errors)
                    
        context={
                    'form':form,'document_entity_records':document_entity_records,"user_name":user_name,
                    "user_role":user_role,"user_profile":user_profile
            }
        return render (request,'DMS/document_entity.html',context)


@custom_login_required
def document_view(request,entity_id,folder_id,document_id):
        try :
                token = request.session['user_token']
                MSID = get_service_plan('document content view')
                data = format_data(MSID,{'document_id':document_id})
                print('data',data)
                response = call_post_method_with_token(BASEURL,ENDPOINT,data,token)
                if response.status_code != 200:
                        print('response error',response)
                # data = response.json()
                content_base64 = response.json()['content']
                url = response.json()['url']
                content= base64.b64depytcode(content_base64)
                # print('content',content)
                # return redirect(url)
                

                context={
                'content':content,'url':url
                }
                return render(request,'DMS/document_view.html',context)
        
        except Exception as error:
                return render(request, "error.html", {"error": error})    



@custom_login_required
def document_version(request,document_id):
        try:
                token=request.session['user_token']
                # user list
           
                # document access list
                doc_access_MSID = get_service_plan('document version')
                doc_access_data = format_data(doc_access_MSID,{'document_id':document_id})
                doc_access_response = call_post_method_with_token(BASEURL,ENDPOINT,doc_access_data,token)
                if doc_access_response.status_code != 200:
                        print('doc_access_response error',doc_access_response)
                doc_access_records = doc_access_response.json()
                print('doc_access_records---',doc_access_records)
                # doc_access = []
                # for data in doc_access_records:
                 

                #         doc_access.append(data)
                # print('doc_access_records',doc_access_records)

              
                context={
                       'doc_access_records':doc_access_records,'document_id':document_id,
                       "BASEURL":BASEURL
                }
                return render (request,'DMS/document_version.html',context)

        except Exception as error:
                return render(request, "error.html", {"error": error})

@custom_login_required
def customer_folder_delete(request,folder_id,entity_id):
        try:
                token = request.session['user_token']
                #document delete
                MSID = get_service_plan('folder delete')
                data = format_data(MSID,{'folder_id':folder_id})
                print('data',data)
                folder_list_response = call_post_method_with_token(BASEURL,ENDPOINT,data,token)
                if folder_list_response.status_code != 200:
                        print('folder_list_response error',folder_list_response)
                else:
                        print(folder_list_response.json())
                return redirect(f'/document_storage/{entity_id}/')
        
        except Exception as error:
                return render(request, "error.html", {"error": error})


#==============
@custom_login_required
def document_delete(request,entity_id,folder_id,document_id):
        try:
                token = request.session['user_token']
                #document delete
                MSID = get_service_plan('document delete')
                data = format_data(MSID,{'document_id':document_id})
                print('data',data)
                folder_list_response = call_post_method_with_token(BASEURL,ENDPOINT,data,token)
                if folder_list_response.status_code != 200:
                        messages.error(request,"Sucessfully deleted")
                        print('folder_list_response error',folder_list_response)
                else:
                        print(folder_list_response.json())
                return redirect(f'/folder/{entity_id}/{folder_id}/')
        
        except Exception as error:
                return render(request, "error.html", {"error": error})


@custom_login_required
def client_folder_delete(request,folder_id,entity_id):
        try:
                token = request.session['user_token']
                #document delete
                MSID = get_service_plan('folder delete')
                data = format_data(MSID,{'folder_id':folder_id})
                print('data',data)
                folder_list_response = call_post_method_with_token(BASEURL,ENDPOINT,data,token)
                if folder_list_response.status_code != 200:
                        print('folder_list_response error',folder_list_response)
                else:
                        print(folder_list_response.json())
                return redirect(f'/document_storage/{entity_id}/')
        
        except Exception as error:
                return render(request, "error.html", {"error": error})


@custom_login_required
def document_edit(request,entity_id,folder_id):
        try:
                token = request.session['user_token']
                #document edit
                MSID = get_service_plan('document edit')
                document_name = request.POST.get('document_name')
                document_id = request.POST.get('document_id')
                print("document_id---",document_id)
                doc_upload = request.FILES['file']
                print("attachment---",doc_upload)
                files = {'files': (doc_upload.name, doc_upload.read())}
                data = {
                        'ms_id':MSID,
                        'ms_payload':json.dumps({'document_id':document_id,'document_name':document_name})
                }                
                print(f'data (type: {type(data)}):', data)
                folder_list_response = call_post_method_with_token(BASEURL,ENDPOINT,data,token,files)
                print("folder_list_response===",folder_list_response)
                if folder_list_response.status_code != 200:
                        print('folder_list_response error',folder_list_response)
                else:
                        print(folder_list_response.json())
                return redirect(f'/folder/{entity_id}/{folder_id}/')
        
        except Exception as error:
                return render(request, "error.html", {"error": error})
