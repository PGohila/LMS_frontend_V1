import json
from django.contrib import messages
from django.shortcuts import redirect, render, HttpResponse
from .decorator import custom_login_required
from .models import *
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
import requests
from django.conf import settings
from .forms import *
from django.forms import formset_factory
BASEURL = settings.BASEURL
ENDPOINT = 'micro-service/'
import re
from django.utils.html import escape
from .scripts import *

def get_service_plan(service_plan_id):
    try:
        # Attempt to retrieve the service plan object by description
        ms_table = MS_ServicePlan.objects.get(description=service_plan_id)
        return ms_table.ms_id
    except ObjectDoesNotExist:
        return None
    except MultipleObjectsReturned:
        raise ValueError("Multiple service plans found for description: {}".format(service_plan_id))
    except Exception as error:
        return None
    
def call_post_method_without_token(URL,data):
    api_url = URL
    headers = { "Content-Type": "application/json"}
    response = requests.post(api_url,data=data,headers=headers)
    return response


def call_post_method_with_token_v2(URL, endpoint, data, access_token, files=None):
    api_url = URL + endpoint
    headers = {"Authorization": f'Bearer {access_token}'}

    if files:
      
        response = requests.post(api_url, data=data, files=files, headers=headers)
    else:
        headers["Content-Type"] = "application/json"
        response = requests.post(api_url, data=data, headers=headers)

    if response.status_code in [200, 201]:
        try:
            return {'status_code': 0, 'data': response.json()}
        except json.JSONDecodeError:
            return {'status_code': 1, 'data': 'Invalid JSON response'}
    else:
        try:
            return {'status_code': 1, 'data': response.json()}
        except json.JSONDecodeError:
            return {'status_code': 1, 'data': 'Something went wrong'}

# ====================== Login =============================
# def login(request):
#     try:
#         # Check if the request method is POST
#         if request.method == "POST":
#             username = request.POST.get('username')
#             password = request.POST.get('password')
#             payload = {        
#                 "username" : username,
#                 "password" : password
#             }
#             # Convert payload to JSON format
#             json_payload = json.dumps(payload)
#             ENDPOINT = 'api/token/'
#             login_response = call_post_method_without_token(BASEURL+ENDPOINT,json_payload)
#             print('login_response',login_response)
#             if login_response.status_code == 200:
#                 login_tokes = login_response.json()
#                 request.session['user_token']=login_tokes['access']

#                 return redirect('company_selecting')
#             else:
#                 login_tokes = login_response.json()
#                 login_error='Invalid Username and Password'
#                 context={"login_error":login_error}
#                 return render(request, 'login.html',context)
          
#         return render(request, 'login.html')
#     except Exception as error:
#         return HttpResponse(f'<h1>{error}</h1>')

def company_selecting(request):
    try:
        token = request.session['user_token']
        MSID = get_service_plan('view company') # view company
        if MSID is None:
            print('MISID not found')        
        data = {'ms_id':MSID,'ms_payload':{}} 
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        companies = response['data']
        if request.method == "POST":
            company_id = request.POST.get('companies')
          
            request.session['company_id'] = company_id
            return redirect('dashboard')
            

        return render(request,'company_selecting.html',{'companies':companies})
    except Exception as error:
        return render(request, "error.html", {"error": error})   

        
def dashboard(request):
    token = request.session['user_token']
    company_id = request.session.get('company_id')
    MSID = get_service_plan('dashboard records')
    if MSID is None:
        print('MISID not found')        
    data = {
        'ms_id':MSID,'ms_payload':{
            'company_id':company_id
        }
        } 
    json_data = json.dumps(data)
    response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
    print('response',response)
    records = response['data']
    user_data = request.session['user_data']
    
    
    return render(request, 'dashboard.html',{'records':records,'user_data':user_data})

# ================== create company =========================
def company_create(request):
    try:
        token = request.session['user_token']
        form = CompanyForm()

        if request.method == "POST":
            form = CompanyForm(request.POST)
            if form.is_valid():
                MSID = get_service_plan('create company')
                if MSID is None:
                    print('MISID not found')      
                cleaned_data = form.cleaned_data
                if cleaned_data['incorporation_date']:
                    cleaned_data['incorporation_date'] = cleaned_data['incorporation_date'].strftime('%Y-%m-%d')   
                data = {'ms_id':MSID,'ms_payload':cleaned_data} 
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
          
                if response['status_code'] ==  0:                  
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('company')
                else:
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 
        context = { 'form':form,"save":True}
        return render(request, 'company/company.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def company_view(request):
    try:
        token = request.session['user_token']
        # getting all companies
        MSID = get_service_plan('view company')
        if MSID is None:
            print('MISID not found')
        payload_form = {}
        data = {'ms_id':MSID,'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        master_view = response['data']
        context = { "company_view_active":"active","records":master_view,"View":True
        }
        return render(request, 'company/company_view.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def company_edit(request,pk):
    try:
        token = request.session['user_token']
        MSID= get_service_plan('view company')
        if MSID is None:
            print('MISID not found')
        payload_form = {"company_id":pk}    
        data = {'ms_id':MSID,'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        master_type_edit = response['data'][0]
        
        form = CompanyForm(initial=master_type_edit)

        if request.method == 'POST':
            MSID = get_service_plan('update company')
            if MSID is None:
                print('MISID not found')
            form = CompanyForm(request.POST,)
            if form.is_valid():
                cleaned_data = form.cleaned_data          
                cleaned_data['company_id'] = pk    
                data = {'ms_id':MSID,'ms_payload':cleaned_data}
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                if response['status_code'] == 0:
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('company')
                else:
                    # return JsonResponse({'error': 'Failed to save form data'}, status=400)
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 

        context = {   
            "company_view_active":"active",
            "form":form,
            "edit":True,
        }
        return render(request, 'company/company.html',context)   
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def company_delete(request,pk):
    try:
        token = request.session['user_token']
        MSID= get_service_plan('delete company')
        if MSID is None:
            print('MISID not found') 
        payload_form = {"company_id":pk}
        data = {'ms_id':MSID,'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 0:
            messages.info(request, "Well Done..! Application Submitted..")
            return redirect('company')
        else:
            messages.info(request, "Oops..! Application Failed to Submitted..")
    except Exception as error:
        return render(request, "error.html", {"error": error}) 

# ======================== Customer Management ============================

def customer_create(request):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        
        form = CustomerForm()

        # getting all customer based on Company 
        MSID = get_service_plan('view customer') # view_customer
        if MSID is None:
            print('MISID not found')
        data = {'ms_id':MSID, 'ms_payload':{'company_id':company_id}}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        master_view = response['data']

        if request.method == "POST":
            form = CustomerForm(request.POST)
            if form.is_valid():
                MSID = get_service_plan('create customer') # create_customer
                if MSID is None:
                    print('MISID not found')      
                cleaned_data = form.cleaned_data
                cleaned_data['company_id'] = company_id
                cleaned_data['dateofbirth'] = cleaned_data['dateofbirth'].strftime('%Y-%m-%d')
                cleaned_data['expiry_date'] = cleaned_data['expiry_date'].strftime('%Y-%m-%d')
                     
                data = {'ms_id':MSID,'ms_payload':cleaned_data} 
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                if response['status_code'] ==  0:                  
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('customer')
                else:
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print("form.errors",form.errors)
                messages.info(request, str(form.errors))
        
        context = { 'form':form,'records':master_view,"save":True}
        return render(request, 'customer_management/customer.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def customer_view(request):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        MSID = get_service_plan('view customer')
        if MSID is None:
            print('MISID not found')
        payload_form = {'company_id':company_id}
        data = {'ms_id':MSID,'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        print("response",response)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        master_view = response['data']
        context = {   
            "customer_view_active":"active",
            "records":master_view,
            "View":True
        }
        return render(request, 'customer_management/customer_view.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def customer_edit(request,pk):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')   
        MSID = get_service_plan('view customer')
        if MSID is None:
            print('MISID not found')
        payload_form = {"customer_id":pk}    
        data = {'ms_id':MSID,'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_type_edit = response['data'][0]
        
        form = CustomerForm(initial=master_type_edit)
        if request.method == 'POST':
            MSID= get_service_plan('update customer')
            if MSID is None:
                print('MISID not found')
            form = CustomerForm(request.POST)
            if form.is_valid():
                cleaned_data = form.cleaned_data          
                cleaned_data['customer_id'] = pk    
                cleaned_data['dateofbirth'] = cleaned_data['dateofbirth'].strftime('%Y-%m-%d')
                cleaned_data['expiry_date'] = cleaned_data['expiry_date'].strftime('%Y-%m-%d')
                cleaned_data['company_id'] = company_id
                   
                data={
                    'ms_id':MSID,
                    'ms_payload':cleaned_data
                }
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                if response['status_code'] == 0:
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('customer_view')
                else:
                    # return JsonResponse({'error': 'Failed to save form data'}, status=400)
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 

        context = {   
            "customer_view_active":"active",
            "form":form,
            "edit":True,
        }
        return render(request, 'customer_management/customer.html',context)   
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def customer_delete(request,pk):
    try:
        token = request.session['user_token']
        MSID= get_service_plan('delete customer')
        if MSID is None:
            print('MISID not found') 
        payload_form = { "customer_id":pk}
        data = {
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 0:
            
            messages.info(request, "Well Done..! Application Submitted..")
            return redirect('customer_view')
        else:
            messages.info(request, "Oops..! Application Failed to Submitted..")
    except Exception as error:
        return render(request, "error.html", {"error": error}) 

# =========== customer document =====================
      

def customer_list(request):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')

        # getting all customer data 
        MSID = get_service_plan('view customer') # view_customer
        if MSID is None:
            print('MSID not found')
        data = {'ms_id': MSID,'ms_payload': {'company_id':company_id}}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        # Check if the response contains data
        if 'data' in response:
            customer_records = response['data']
        else:
            print('Data not found in response')

        return render(request,'customer_management/customer_list.html',{'records':customer_records})
    except Exception as error:
        return render(request, "error.html", {"error": error}) 

def uploadmultidocument_customer(request,pk): #pk = customer id
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')

        # getting all customer data 
        MSID = get_service_plan('view customer') # view_customer
        if MSID is None:
            print('MSID not found')
        data = {'ms_id': MSID,'ms_payload': {'customer_id':pk}}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        
        customer_records = response['data'][0]

        # getting identification Type
        MSID = get_service_plan('view identificationtype') # view_identificationtype
        if MSID is None:
            print('MSID not found')
        data = {'ms_id': MSID,'ms_payload': {'company_id':company_id}}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})

        document_type = response['data']
        if request.method == "POST":
            is_active = request.POST.getlist('is_active')
            documenttype = request.POST.getlist('document_type')
            documentfile = request.FILES.getlist('documentfile')
            description = request.POST.getlist('description')

            for index,data1 in enumerate(documentfile):
                MSID = get_service_plan('create customerdocuments') # create_customerdocuments
                if MSID is None:
                    print('MISID not found')     
                
                payload = {'company_id':company_id,'customer_id':pk, 'document_type_id':documenttype[index],'is_active': True,'description':description[index]}
                files = {}
                documentfile1 = documentfile[index]
                if documentfile1:
                    files['attachment'] = (documentfile1.name, documentfile1, documentfile1.content_type)
                data = {'ms_id': MSID, 'ms_payload': json.dumps(payload)}
                response = call_post_method_with_token_v2(BASEURL, ENDPOINT, data, token, files)   
            
                if response['status_code'] ==  1:                  
                    return render(request,'error.html',{'error':str(response['data'])})
              
            return redirect('customerlist')

        context = {'customer_records':customer_records,'document_type':document_type}
        return render(request,'customer_management/Upload_multidocments.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error}) 


def customer_view_fordoc(request):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        # getting all customer data 
        MSID = get_service_plan('view customerdocuments') # view_customerdocuments
        if MSID is None:
            print('MSID not found')
        data = {'ms_id': MSID,'ms_payload': {'company_id':company_id}}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        # Check if the response contains data
        if 'data' in response:
            customer_records = response['data']
        else:
            print('Data not found in response')
        return render(request, 'customer_management/view_documents.html',{'BASEURL':BASEURL,'customer_records':customer_records}) 
    except Exception as error:
        return render(request, "error.html", {"error": error})   

# ================================= Loan Applications ========================

def loanapplication_create(request):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')

        # getting customers based on 
        MSID = get_service_plan('view customer') # view_customer
        if MSID is None:
            print('MSID not found')
        data = {'ms_id': MSID,'ms_payload': {'company_id':company_id}}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        # Check if the response contains data
        if 'data' in response:
            customer_id_records = response['data']
        else:
            print('Data not found in response')
        
        
        MSID = get_service_plan('view loantype') # view_loantype
        if MSID is None:
            print('MSID not found')
        data = {'ms_id': MSID,'ms_payload': {'company_id':company_id}}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        loantype_records = response['data']
        # Check if the response contains data
        if 'data' in response:
            loantype_records = response['data']
        else:
            print('Data not found in response')
        

        form = LoanapplicationForm(customer_id_choice=customer_id_records,loantype_choice=loantype_records)
        if request.method == "POST":
            form = LoanapplicationForm(request.POST,customer_id_choice=customer_id_records,loantype_choice=loantype_records)
            if form.is_valid():
                MSID= get_service_plan('create loanapplication') # create_loanapplication
                if MSID is None:
                    print('MISID not found')      
                cleaned_data = form.cleaned_data
                cleaned_data['company_id'] = company_id
                cleaned_data['repayment_date'] = cleaned_data['repayment_date'].strftime('%Y-%m-%d')

                data = {'ms_id':MSID,'ms_payload':cleaned_data} 
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                print("========================",response)
                if response['status_code'] ==  0:                  
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('loanapplication')
                else:
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 
        
        context = {      
            'form':form,"save":True
        }
        return render(request, 'loan_application/loanapplication.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def loanapplication_view(request):
    try:
        token = request.session['user_token']  
        company_id = request.session.get('company_id')
        MSID = get_service_plan('view loanapplication')
        if MSID is None:
            print('MISID not found')
        payload_form = { 'company_id':company_id  }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        master_view = response['data']

        context={   
            "loanapplication_view_active":"active",
            "records":master_view,
            "View":True
        }
        return render(request, 'loan_application/loanapplication_view.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def loanapplication_summary(request,pk): # pk = application id
    try:
        token = request.session['user_token']  
        company_id = request.session.get('company_id')
        MSID = get_service_plan('view loanapplication') # view_loanapplication
        if MSID is None:
            print('MISID not found')
        payload_form = { 'loanapplication_id':pk  }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        master_view = response['data'][0]

        context={   
            "loanapplication_view_active":"active",
            "records":master_view,
            "View":True
        }
        return render(request, 'loan_application/loanapplication_summary.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})  

def loanapplication_edit(request,pk):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        
        MSID = get_service_plan('view customer')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {'company_id':company_id}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})

        # Check if the response contains data
        if 'data' in response:
            customer_id_records = response['data']
        else:
            print('Data not found in response')
       
        MSID = get_service_plan('view loantype')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {'company_id':company_id}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
    

        # Check if the response contains data
        if 'data' in response:
            loantype_records = response['data']
        else:
            print('Data not found in response')

        MSID = get_service_plan('view loanapplication')
        if MSID is None:
            print('MISID not found')
        payload_form = {
            "loanapplication_id":pk
        }    
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        master_type_edit = response['data'][0]
        
        form = LoanapplicationForm(initial=master_type_edit,customer_id_choice=customer_id_records,loantype_choice=loantype_records)
        if request.method == 'POST':
            MSID= get_service_plan('update loanapplication')
            if MSID is None:
                print('MISID not found')
            form = LoanapplicationForm(request.POST,customer_id_choice=customer_id_records,loantype_choice=loantype_records)
            if form.is_valid():
                cleaned_data = form.cleaned_data  
                cleaned_data['company_id']=company_id        
                cleaned_data['loanapplication_id'] = pk   
                del cleaned_data['repayment_date'] 

                   
                data={
                    'ms_id':MSID,
                    'ms_payload':cleaned_data
                }
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                if response['status_code'] == 0:
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('loanapplication')
                else:
                    # return JsonResponse({'error': 'Failed to save form data'}, status=400)
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 

        context={   
            "loanapplication_view_active":"active",
            "form":form,
            "edit":True,
        }
        return render(request, 'loan_application/loanapplication.html',context)   
    except Exception as error:
        return render(request, "error.html", {"error": error})    


def loanapplication_delete(request,pk):
    try:
        token = request.session['user_token']
        MSID = get_service_plan('delete loanapplication')
        if MSID is None:
            print('MISID not found') 
        payload_form = {"loanapplication_id":pk}
        data = {'ms_id':MSID,'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 0:
            messages.info(request, "Well Done..! Application Submitted..")
            return redirect('loanapplication')
        else:
            messages.info(request, "Oops..! Application Failed to Submitted..")
    except Exception as error:
        return render(request, "error.html", {"error": error}) 

def view_loan_applications(request):
    try:
        token = request.session['user_token']  
        company_id = request.session.get('company_id')
        MSID = get_service_plan('view loanapplication')
        if MSID is None:
            print('MISID not found')
        payload_form = { 'company_id':company_id  }
        data = { 'ms_id':MSID,'ms_payload':payload_form }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        master_view = response['data']
        context = { "records":master_view, "View":True}
        return render(request,'loan_application/view_loan_applications.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})


def application_status_tracking(request,pk): # pk = application id 
    try:
        token = request.session['user_token']  
        company_id = request.session.get('company_id')
        MSID = get_service_plan('view loanapplication') # view_loanapplication
        if MSID is None:
            print('MISID not found')
        payload_form = { 'loanapplication_id':pk }
        data = { 'ms_id':MSID,'ms_payload':payload_form }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        master_view = response['data'][0]
        context = {'application':master_view}
        return render(request,'loan_application/status_tracking.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error}) 



# ========================== Loan Approval menus ==============================

# loan eligibilities check
# disply active and document verified applications list
def show_active_applications(request): 
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        # ================== check over all submited applications eligibility ==============================

        MSID = get_service_plan('check loan eligibilities forall') # check_loan_eligibilities_forall
        if MSID is None:
            print('MISID not found')
        payload_form = {'company_id':company_id}    
        data = {
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        application_records = response['data']

        MSID = get_service_plan('view loanapplication') # view_loanapplication
        if MSID is None:
            print('MISID not found')
        payload_form = {'company_id':company_id}    
        data = {
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        application_records = response['data']
        
        # Filter by specific application statuses
        active_data = [entry for entry in application_records if entry['is_active'] == True]
        eligible_data = [entry for entry in application_records if entry['is_eligible'] == True and entry['is_active'] == True]
        ineligible_data = [entry for entry in application_records if entry['is_eligible'] == False and entry['is_active'] == True]
        print("=============",active_data)
        print("=============",eligible_data)
        print("=============",ineligible_data)
        
        context =  {'is_eligible':True,'submitted_data':active_data,'eligible_data':eligible_data,'ineligible_data':ineligible_data}
        return render(request,"loan_approval/verified_applications.html",context)
    except Exception as error:
        return render(request, "error.html", {"error": error}) 

def eligibility_status(request,pk): # pk = application_id
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        # getting loan eligibility result
        MSID = get_service_plan('check loan eligibilities') # check_loan_eligibilities
        if MSID is None:
            print('MISID not found')
        payload_form = {'application_id':pk}    
        data = {
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        eligibility_status = response['data'][0]

        context = {'is_eligible':eligibility_status['eligible_status'],'reject_reason':eligibility_status['errors']}
        return render(request,"loan_approval/eligibility_status.html",context)
    except Exception as error:
        return render(request, "error.html", {"error": error}) 

#  loan risk assesssment list 
def loan_risk_assessment_list(request):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        MSID = get_service_plan('loan risk assessment list') # loan_risk_assessment_list
        if MSID is None:
            print('MISID not found')
        payload_form = {'company_id':company_id}    
        data = {
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        loan_applications_with_risk = response['data']
        print("loan_applications_with_risk",loan_applications_with_risk,)
        context =  {'records':loan_applications_with_risk}
        return render(request,"loan_approval/loan_risk_assessment_list.html",context)
    except Exception as error:
        return render(request, "error.html", {"error": error}) 

# Function to display detailed risk assessment for a specific loan application
def loan_risk_assessment_detail(request, pk): # pk = application_id
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        MSID = get_service_plan('loan risk assessment detail') # loan_risk_assessment_detail
        if MSID is None:
            print('MISID not found')
        payload_form = {'application_id':pk}    
        data = {
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        master_type_edit = response['data'][0]
        context =  {'records':master_type_edit}
        return render(request,"loan_approval/loan_risk_assessment_detail.html",context)
    except Exception as error:
        return render(request, "error.html", {"error": error}) 

# disply all active applications 
def document_varification(request):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        # getting all active applications 
        MSID = get_service_plan('view loanapplication') # view_loanapplication
        if MSID is None:
            print('MISID not found') 
        payload_form = {"company_id":company_id}
        data = {'ms_id':MSID,'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        active_applications = [applications for applications in response['data'] if applications['is_active'] == True]
        verified_applications = [applications for applications in response['data'] if applications['document_verified'] == True]
        unverified_applications = [applications for applications in response['data'] if applications['document_verified'] == False]
        context = {'active_applications':active_applications,'verified_applications':verified_applications,'unverified_applications':unverified_applications}
        return render(request,"loan_approval/document_verification.html",context)
    except Exception as error:
        return render(request, "error.html", {"error": error}) 

def verify_documents(request,pk): #pk = application id
    try:

        token = request.session['user_token']
        company_id = request.session.get('company_id')

        # getting application data
        MSID = get_service_plan('view loanapplication') # view_loanapplication
        if MSID is None:
            print('MISID not found') 
        payload_form = {"loanapplication_id":pk}
        data = {'ms_id':MSID,'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})

        application_data = response['data'][0]

        # getting customer data
        MSID = get_service_plan('view customer') # view_customer
        if MSID is None:
            print('MISID not found') 
        payload_form = {"customer_id":application_data['customer_id']['id']}
        data = {'ms_id':MSID,'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})

        customer_data = response['data'][0]

        # getting customer related records
        MSID = get_service_plan('getting verified ducuments') # getting_verified_ducuments
        if MSID is None:
            print('MISID not found') 
        payload_form = {"company_id":company_id,'customer_id':application_data['customer_id']['id']}
        data = {'ms_id':MSID,'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        
        customer_doc = response['data']
        
        # getting collateral document using application Id
        MSID = get_service_plan('view collateraldocument') # view_collateraldocument
        if MSID is None:
            print('MISID not found') 
        payload_form = {"loan_application_id":pk}
        data = {'ms_id':MSID,'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})

        collateraldoc_data = response['data']

        
        if request.method == "POST":

            MSID = get_service_plan('customerdoc verification') # customerdoc_verification
            if MSID is None:
                print('MISID not found') 
            payload_form = {"customerdoc_id":pk}
            data = {'ms_id':MSID,'ms_payload':payload_form}
            json_data = json.dumps(data)
            response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
            if response['status_code'] == 1:
                return render(request,'error.html',{'error':str(response['data'])})
            return redirect("document_varification")

        context = {'customer_data':customer_data,'documents':customer_doc,'BASEURL':BASEURL,'collateraldoc_data':collateraldoc_data}
        return render(request,"loan_approval/document_verify.html",context)
    except Exception as error:
        return render(request, "error.html", {"error": error}) 

def loan_approval_view(request):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        MSID = get_service_plan('getting approved rejected applications') # getting_approved_rejected_applications
        if MSID is None:
            print('MISID not found')
        payload_form = {'company_id':company_id}    
        data = {'ms_id':MSID,'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        active_applications = [applications for applications in response['data'] if applications['is_active'] == True and applications['application_status'] == 'Submitted']
        approved_applications = [applications for applications in response['data'] if applications['is_active'] == True and applications['application_status'] == 'Approved']
        rejected_applications = [applications for applications in response['data'] if applications['is_active'] == True and applications['application_status'] == 'Rejected']
        context =  {'active_applications':active_applications,'approved_applications':approved_applications,'rejected_applications':rejected_applications}
        return render(request,"loan_approval/pending_approvals.html",context)
    except Exception as error:
        return render(request, "error.html", {"error": error})

def loan_approval(request,pk): # application id
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        # getting application data
        MSID = get_service_plan('view loanapplication') # view_loanapplication
        if MSID is None:
            print('MISID not found') 
        payload_form = {"loanapplication_id":pk}
        data = {'ms_id':MSID,'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})

        application_data = response['data'][0]

        # getting customer data
        MSID = get_service_plan('view customer') # view_customer
        if MSID is None:
            print('MISID not found') 
        payload_form = {"customer_id":application_data['customer_id']['id']}
        data = {'ms_id':MSID,'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})

        customer_data = response['data'][0]

        if request.method == "POST":
            status = request.POST.get('approveBtn')
            status1 = request.POST.get('Decline')
            rejecting_reason = request.POST.get('reason')
            if status == 'Approved':
                MSID = get_service_plan('loan approval') # loan_approval
                if MSID is None:
                    print('MISID not found') 
                payload_form = {'company_id':company_id,'loanapp_id':pk,'approval_status' : "Approved"}
                data = {'ms_id':MSID,'ms_payload':payload_form}
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                print('response',response)
                if response['status_code'] == 1:
                    return render(request,'error.html',{'error':str(response['data'])})
                return redirect('loanapprovalview')
            elif status1 == 'Decline':
                MSID = get_service_plan('loan approval') # loan_approval
                if MSID is None:
                    print('MISID not found') 
                payload_form = {'loanapp_id':pk,'company_id':company_id,'approval_status' : "Rejected",'rejected_reason':rejecting_reason}
                data = {'ms_id':MSID,'ms_payload':payload_form}
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                if response['status_code'] == 1:
                    return render(request,'error.html',{'error':str(response['data'])})
                return redirect('loanapprovalview')
            else:
                pass
            
        context = {'application_data':application_data,'customer_data':customer_data}
        return render(request,"loan_approval/loan_approval.html",context)
    except Exception as error:
        return render(request, "error.html", {"error": error})

# ================== Loan Agreeement =========================
# generate loan agreement 

def list_approved_applications(request):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')

        MSID = get_service_plan('getting approved applications') # getting_approved_applications
        if MSID is None:
            print('MISID not found') 
        payload_form = {'company_id':company_id}
        data = {'ms_id':MSID,'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        print('response',response)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        context = {'records':response['data']}
        return render(request,"loan_agreement/approved_list.html",context)
    except Exception as error:
        return render(request, "error.html", {"error": error})

def loan_list(request):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')

        MSID = get_service_plan('getting loan tranches') # getting_loan_tranches
        if MSID is None:
            print('MSID not found')
        payloads = {'company_id':company_id}
        data = {'ms_id': MSID,'ms_payload': payloads}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        loan_details = response['data']

        # MSID = get_service_plan('create loanvaluechain') # create_loanvaluechain
        # if MSID is None:
        #     print('MSID not found')
        # payloads = {'company_id':company_id}
        # data = {'ms_id': MSID,'ms_payload': payloads}
        # json_data = json.dumps(data)
        # response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        # if response['status_code'] == 1:
        #     return render(request,'error.html',{'error':str(response['data'])})
        
        context = {'loan_details':loan_details}
        return render(request,'valuechain/loan_list.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})

# def loan_list(request):
#     # try:
#         token = request.session['user_token']
#         MSID = get_service_plan('view loan')
#         if MSID is None:
#                 print('MISID not found') 
#         payload_form = {
#         }
#         data = {
#             'ms_id':MSID,
#             'ms_payload':payload_form
#             }
#         json_data = json.dumps(data)
#         response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
#         print('response',response)
#         if response['status_code'] == 1:
#             return render(request,'error.html',{'error':str(response['data'])})
#         context = {'records':response['data']}
#         return render(request,"valuechain/loan_list.html",context)
#     # except Exception as error:
#     #     return render(request, "error.html", {"error": error})

def account_list(request,id):
    try:
        token = request.session['user_token']
        MSID = get_service_plan('account list')
        if MSID is None:
                print('MISID not found') 
        payload_form = {
            "loan_id":id
        }
        data = {
            'ms_id':MSID,
            'ms_payload':payload_form
            }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        print('response',response)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        print('response["data"]',response['data'])
        context = {
            'records':response['data']
            }
        print("response['data']",response['data'])
        return render(request,"loan_approval/loans.html",context)    
    except Exception as error:
        return render(request, "error.html", {"error": error})


def create_agreement(request,pk):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        # getting loan application data
        MSID = get_service_plan('view loan') # view_loan
        if MSID is None:
            print('MISID not found') 
        payload_form = {'loanapp_id':pk}
        data = {'ms_id':MSID,'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        print('loan aplication',response)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        loan_data = response['data'][0]

        # getting loan application data
        MSID = get_service_plan('view template') # view_loan
        if MSID is None:
            print('MISID not found') 
        data = {'ms_id':MSID,'ms_payload':{}}
        json_data = json.dumps(data)
        template_response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if template_response['status_code'] == 1:
            return render(request,'error.html',{'error':str(template_response['data'])})
        template_records = template_response['data']
        print('template_records',template_records)
        initial = {'customer_id':loan_data['customer']['customer_id'],'loan_id':loan_data['loan_id'],'loanapp_id':loan_data['loanapp_id']['application_id']}
        form = LoanAgreementForm(initial=initial,template_choice=template_records)
        if request.method == "POST":
            form = LoanAgreementForm(request.POST,template_choice=template_records)
            if form.is_valid():
                MSID = get_service_plan('create loanagreement') # create_loanagreement
                if MSID is None:
                    print('MISID not found')      
                cleaned_data = form.cleaned_data
                del cleaned_data['customer_id']
                del cleaned_data['loan_id']
                del cleaned_data['loanapp_id']

                cleaned_data['company_id'] = company_id
                
                cleaned_data['customer_id'] = loan_data['customer']['id']
                cleaned_data['loan_id'] = loan_data['id']
                cleaned_data['loanapp_id'] = loan_data['loanapp_id']['id']
                agreement_template = cleaned_data['agreement_template'] 

                return redirect(f"/agreement_review/{pk}/{agreement_template}/")
                data = {'ms_id':MSID,'ms_payload':cleaned_data} 
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                print("response",response)
                if response['status_code'] ==  0:                  
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('list_agreement')
                else:
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 
            

        context = {'form':form}
        return render(request,"loan_agreement/loan_agreement.html",context)
    except Exception as error:
        return render(request, "error.html", {"error": error})

def agreement_review(request,loanapp_id,template_id):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        # getting loan application data
        MSID = get_service_plan('template fields') # view_loan
        if MSID is None:
            print('MISID not found') 
        payload_form = {'loan_id':loanapp_id,'template_id':template_id}
        data = {'ms_id':MSID,'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        placeholders = response['data']
        print('placeholders',placeholders)
      
        if request.method == "POST":
            for data in placeholders:
                value = request.POST.get(data.get('name'))
                data['value']=value
            
            MSID = get_service_plan('agreement draft') # create_loanagreement
            if MSID is None:
                print('MISID not found')      
           
            data = {'ms_id':MSID,'ms_payload':{'loan_id':loanapp_id,'agreement_template':template_id,'agreement_template_value':placeholders}} 
            json_data = json.dumps(data)
            response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
            print("response",response)
            if response['status_code'] ==  0:                  
                messages.info(request, "Well Done..! Application Submitted..")
                return redirect('list_agreement')
            else:
                messages.info(request, "Oops..! Application Failed to Submitted..")
           

        context = {
            'placeholders':placeholders
            }
        return render(request,"loan_agreement/loan_agreement_preview1.html",context)
    except Exception as error:
        return render(request, "error.html", {"error": error})


def list_agreement(request):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        # getting loan application data
        MSID = get_service_plan('view loanagreement') # view_loanagreement
        if MSID is None:
            print('MISID not found') 
        payload_form = {'company_id':company_id}
        data = {'ms_id':MSID,'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        agreement_data = response['data']
 
        context = {'records':agreement_data}
        return render(request,"loan_agreement/list_agreement.html",context)
    except Exception as error:
        return render(request, "error.html", {"error": error})

def agreement_confirmation(request,pk): # pk = agreement id
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        if request.method == "POST":
            approve = request.POST.get('Confirmed')
            rejected = request.POST.get('Reject')
            if approve == "Confirmed":
                MSID = get_service_plan('loanagreement confirmation') # loanagreement_confirmation
                if MSID is None:
                    print('MISID not found') 
                payload_form = {'company_id':company_id,'loanagreementid':pk,'status':'Completed'}
                data = {'ms_id':MSID,'ms_payload':payload_form}
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                if response['status_code'] == 1:
                    return render(request,'error.html',{'error':str(response['data'])})
                return redirect('list_agreement')
            elif rejected == "terminated":
                MSID = get_service_plan('loanagreement confirmation') # loanagreement confirmation
                if MSID is None:
                    print('MISID not found') 
                payload_form = {'company_id':company_id,'loanagreementid':pk,'status':'Terminated'}
                data = {'ms_id':MSID,'ms_payload':payload_form}
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                if response['status_code'] == 1:
                    return render(request,'error.html',{'error':str(response['data'])})
                return redirect('list_agreement')
        else:
            MSID = get_service_plan('view loanagreement') # view_loanagreement
            if MSID is None:
                print('MISID not found') 
            payload_form = {'loanagreement_id':pk}
            data = {'ms_id':MSID,'ms_payload':payload_form}
            json_data = json.dumps(data)
            response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
            if response['status_code'] == 1:
                return render(request,'error.html',{'error':str(response['data'])})
            agreement_data = response['data'][0]
            # print('agreement_data',agreement_data)
            template = tag_replacement(agreement_data.get('agreement_template').get('content'),agreement_data.get('agreement_template_value'))
            

        context = {
            'template':template,'agreement_id':pk,'agreement_data':agreement_data
        }
        return render(request,'loan_agreement/agreement_confirmation.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})
        

def agreement_signature_update(request,agreement_id): # pk = agreement id
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        if request.method == "POST":
            borrower_signature = request.POST.get('borrower_signature')
            lender_signature = request.POST.get('lender_signature')
            
            MSID = get_service_plan('agreement signature update') # loanagreement confirmation
            if MSID is None:
                print('MISID not found') 
            payload_form = {'agreement_id':agreement_id}
            if borrower_signature:
                payload_form['borrower_signature']=borrower_signature
            if lender_signature:
                payload_form['lender_signature']=lender_signature
            data = {'ms_id':MSID,'ms_payload':payload_form}
            json_data = json.dumps(data)
            response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
            if response['status_code'] == 1:
                return render(request,'error.html',{'error':str(response['data'])})
        return redirect(f'/agreement_confirmation/{agreement_id}')
        

    except Exception as error:
        return render(request, "error.html", {"error": error})
        

def edit_agreement(request,pk):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')

        # getting loan agreement data
        MSID = get_service_plan('view loanagreement') # view_loanagreement
        if MSID is None:
            print('MISID not found') 
        payload_form = {'loanagreement_id':pk}
        data = {'ms_id':MSID,'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        agreement_data = response['data'][0]

        initial = {'customer_id':agreement_data['customer_id']['customer_id'],'loan_id':agreement_data['loan_id']['loan_id'],'loanapp_id':agreement_data['loanapp_id']['application_id'],'agreement_terms':agreement_data['agreement_terms'],'maturity_date':agreement_data['maturity_date']}
        form = LoanAgreementForm(initial = initial)
        if request.method == 'POST':
            MSID = get_service_plan('update loanagreement') # update_loanagreement
            if MSID is None:
                print('MISID not found')
            
            form = LoanAgreementForm(request.POST)
            if form.is_valid():
                cleaned_data = form.cleaned_data          
                cleaned_data['loanagreement_id'] = pk   
                cleaned_data['company_id'] = company_id
                cleaned_data['customer_id'] = agreement_data['customer_id']['id']
                cleaned_data['loan_id'] = agreement_data['loan_id']['id']
                cleaned_data['loanapp_id'] = agreement_data['loanapp_id']['id']
                if cleaned_data['maturity_date']:
                    cleaned_data['maturity_date'] = cleaned_data['maturity_date'].strftime('%Y-%m-%d')
                else:
                    cleaned_data['maturity_date'] = None
                data = {'ms_id':MSID,'ms_payload':cleaned_data}
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                if response['status_code'] == 0:
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect(f'/agreementconfirmation/{pk}/')
                else:
                    # return JsonResponse({'error': 'Failed to save form data'}, status=400)
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 

        context = {'records':agreement_data,'form':form}
        return render(request,'loan_agreement/loan_agreement.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})

#============================= Loan Accounts OverView =========================

# =================================== loan disbursement ==================================
# this function for display all completed agreements 
def disbursement_request(request):
    try:

        token = request.session['user_token']
        company_id = request.session.get('company_id')
        
        # getting loan application data
        MSID = get_service_plan('getting completed agreement') # getting_completed_agreement
        
        if MSID is None:
            print('MISID not found') 
        payload_form = {'company_id':company_id}
        
        data = {'ms_id':MSID,'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        loan_data = response['data']
        print("loan_data",loan_data)
        context = {'records':loan_data}
        return render(request,'disbursement/disbursement_request.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})

# this function for disbursement approval
def disply_agreed_agreement(request,pk):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')

        # getting loan agreement data
        MSID = get_service_plan('view loan') # view_loan
        if MSID is None:
            print('MISID not found') 
        payload_form = {'loan_id':pk}
        data = {'ms_id':MSID,'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        agreement_data = response['data'][0]
        
        context = {'agreement_data':agreement_data}
        return render(request,'disbursement/agrement_approved.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})


def disply_loans(request):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        # getting loan agreement data
        MSID = get_service_plan('getting completed agreement') # getting_completed_agreement
        if MSID is None:
            print('MISID not found') 
        payload_form = {'company_id':company_id}
        data = {'ms_id':MSID,'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        loan_data = response['data']
        print('loan_data',loan_data)

        context = {'records':loan_data}
        return render(request,'disbursement/loan_list.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})


#====================== create disbursement =================================

def disbursement_create(request,loanid):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')

        # getting related loan data
        MSID = get_service_plan('view loan') # view_loan
        if MSID is None:
            print('MSID not found')
        data = {'ms_id': MSID,'ms_payload': {'loan_id':loanid}}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        loan_data = response['data'][0]
       

        #  getting customeraccount
        MSID = get_service_plan('getting customeraccount') # getting_customeraccount
        if MSID is None:
            print('MSID not found')
        data = {'ms_id': MSID,'ms_payload': {'customer_id':loan_data['customer']['id']}}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        borroweraccount = response['data'][0]

        if request.method == "POST":
            
            MSID = get_service_plan('create disbursement') # create_disbursement
            if MSID is None:
                print('MISID not found')      
            payloads = {'company_id':company_id,'customer_id':loan_data['customer']['id'],'loan_id':loan_data['id'], 'loan_application_id':loan_data['loanapp_id']['id'], 'amount':request.POST.get('disursement_amount'), 'disbursement_type':loan_data['loanapp_id']['disbursement_type'], 'disbursement_status':request.POST.get('disbursement_status'),'bank':borroweraccount['id']}
            data = {'ms_id':MSID,'ms_payload':payloads} 
            json_data = json.dumps(data)
            response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
            if response['status_code'] ==  0:                  
                messages.info(request, "Well Done..! Application Submitted..")
            return redirect("disply_loans")
         
        context={      
            "save":True,'loan_data':loan_data,'borroweraccount':borroweraccount
        }
        return render(request, 'disbursement/disbursement.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def disbursement_details(request):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')

        MSID = get_service_plan('view disbursement') # view_disbursement
        if MSID is None:
            print('MSID not found')
        data = {'ms_id': MSID,'ms_payload': {'company_id':company_id}}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        disbursement_data = response['data']
        context = {'disbursement_data':disbursement_data}
        return render(request, 'disbursement/disbursement_details.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error}) 

def show_disbursement_details(request,pk): # pk = disbursement id
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        MSID = get_service_plan('view disbursement') # view_disbursement
        if MSID is None:
            print('MSID not found')
        data = {'ms_id': MSID,'ms_payload': {'disbursement_id':pk}}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        disbursement_data = response['data'][0]
        context = {'disbursement_data':disbursement_data}
        return render(request, 'disbursement/disbursement_data.html',context)
    
    except Exception as error:
        return render(request, "error.html", {"error": error}) 

# ======================= colateral management ===========================
def show_loandetails(request):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')

        # getting application data
        MSID = get_service_plan('view loanapplication') # view_loanapplication
        if MSID is None:
            print('MISID not found') 
        payload_form = {'company_id':company_id}
        data = {'ms_id':MSID,'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})

        application_data = [data for data in response['data'] if data['is_active'] == True]
        context = {'records':application_data}
        return render(request,'collateral_management/loan_details.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error}) 

def create_collateral(request, pk):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')

        # getting company wise collateral type
        MSID = get_service_plan('view collateraltype') # view_collateraltype
        if MSID is None:
            print('MSID not found')
        data = {'ms_id': MSID, 'ms_payload': {'company_id': company_id}}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        if response['status_code'] == 1:
            return render(request, "error.html", {"error": response['data']})

        # Check if the response contains data
        if 'data' in response:
            collateral_type_records = response['data']
        else:
            print('Data not found in response')

        # getting company wise loan applications
        MSID = get_service_plan('view loanapplication') # view_loanapplication
        if MSID is None:
            print('MSID not found')
        data = {'ms_id': MSID,'ms_payload': {'loanapplication_id':pk}}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        if response['status_code'] == 1:
            return render(request,"error.html", {"error": response['data']})
        # Check if the response contains data
        if 'data' in response:
            loanapp_id_records = response['data'][0]
        else:
            print('Data not found in response')

        collateral_form = CollateralsForm(collateral_type_choice = collateral_type_records)

        if request.method == 'POST':
            collateral_butn = request.POST.get('collateral_btn')
            attachment_butn = request.POST.get('attachment_btn')

            if collateral_butn == 'collateral_btn':
                collateral_type = request.POST.getlist('collateral_type')
                collateral_value = request.POST.getlist('collateral_value')
                valuation_date = request.POST.getlist('value_date')
                collateral_status = request.POST.getlist('collateral_status')
                insurance_status = request.POST.getlist('insurance_status')
                description = request.POST.getlist('description')
                for index,data in enumerate(collateral_type):
                    MSID = get_service_plan('create collaterals') # create_collaterals
                    if MSID is None:
                        print('MSID not found')
                    payload = {'company_id':company_id, 'loanapp_id':pk, 'customer_id':loanapp_id_records['customer_id']['id'], 'collateral_type_id':collateral_type[index], 'collateral_value':collateral_value[index], 
                            'valuation_date': valuation_date[index], 'collateral_status':collateral_status[index], 'insurance_status':insurance_status[index],'description':description[index]}
                    data = {'ms_id': MSID,'ms_payload': payload}
                    json_data = json.dumps(data)
                    response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
                    if response['status_code'] == 1:
                        return render(request,"error.html", {"error": response['data']})
                    return redirect(f'/create_collateral/{pk}/')
            elif attachment_butn == 'attachment_btn':
                document_name = request.POST.getlist('document_name')
                attachment = request.FILES.getlist('uploaded_file')
                description = request.POST.getlist('description1')

                for index,data in enumerate(document_name):
                    files = {}
                    MSID = get_service_plan('upload collateraldocument') # upload_collateraldocument
                    if MSID is None:
                        print('MSID not found')
                    payload = {'company_id':company_id,'loanapplication_id':pk,'document_name':document_name[index],'desctioption':description[index]}
                    data = {'ms_id': MSID,'ms_payload': json.dumps(payload)}
                    json_data = json.dumps(data)
                    if attachment[index]:
                        files['attachment'] = (attachment[index].name, attachment[index], attachment[index].content_type)
    
                    response = call_post_method_with_token_v2(BASEURL, ENDPOINT, data, token,files)
                    if response['status_code'] == 1:
                        return render(request,"error.html", {"error": response['data']})
                return redirect(f'/create_collateral/{pk}/')
            else:
                pass
    
        context = {
            'forms': collateral_form,
            'collateral_formset': collateral_form,
            'collateral_type': collateral_type_records,
            'loanapplication_records':loanapp_id_records
            
        }
        return render(request, 'collateral_management/create_collateral.html', context)
    except Exception as error:
        return render(request, "error.html", {"error": error}) 


# def collaterals_create(request):
#     try:
#         token = request.session['user_token']
#         company_id = request.session.get('company_id')

#         # getting company wise loan applications
#         MSID = get_service_plan('view loanapplication') # view_loanapplication
#         if MSID is None:
#             print('MSID not found')
#         data = {'ms_id': MSID,'ms_payload': {'company_id':company_id}}
#         json_data = json.dumps(data)
#         response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
#         if response['status_code'] == 1:
#             return render(request,"error.html", {"error": response['data']})
#         # Check if the response contains data
#         if 'data' in response:
#             loanapp_id_records = response['data']
#         else:
#             print('Data not found in response')
       
#         MSID = get_service_plan('view customer') # view_customer
#         if MSID is None:
#             print('MSID not found')
#         data = {'ms_id': MSID,'ms_payload': {'company_id':company_id}}
#         json_data = json.dumps(data)
#         response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
#         if response['status_code'] == 1:
#             return render(request,"error.html", {"error": response['data']})
#         # Check if the response contains data
#         if 'data' in response:
#             customer_id_records = response['data']
#         else:
#             print('Data not found in response')

#         # getting company wise collateral type
#         MSID = get_service_plan('view collateraltype') # view_collateraltype
#         if MSID is None:
#             print('MSID not found')
#         data = {'ms_id': MSID,'ms_payload': {'company_id':company_id}}
#         json_data = json.dumps(data)
#         response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
#         if response['status_code'] == 1:
#             return render(request,"error.html", {"error": response['data']})
#         # Check if the response contains data
#         if 'data' in response:
#             collateral_type_records = response['data']
#         else:
#             print('Data not found in response')

#         form = CollateralsForm(loanapp_id_choice=loanapp_id_records,customer_id_choice=customer_id_records,collateral_type_choice=collateral_type_records)
#         MSID = get_service_plan('view collaterals') # view_collaterals
#         if MSID is None:
#             print('MISID not found')
#         data = {'ms_id':MSID,'ms_payload':{'company_id':company_id}}
#         json_data = json.dumps(data)
#         response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
#         if response['status_code'] == 1:
#             return render(request,"error.html", {"error": response['data']})
#         master_view = response['data']
#         if request.method == "POST":
#             form = CollateralsForm(request.POST, request.FILES,loanapp_id_choice=loanapp_id_records,customer_id_choice=customer_id_records,collateral_type_choice=collateral_type_records)
#             if form.is_valid():
                
#                 MSID = get_service_plan('create collaterals') # create_collaterals
#                 if MSID is None:
#                     print('MISID not found')      
#                 cleaned_data = form.cleaned_data
#                 cleaned_data['valuation_date'] = cleaned_data['valuation_date'].strftime('%Y-%m-%d')
#                 cleaned_data['company_id'] = company_id 
#                 files = {}
#                 # get valuation report file

#                 valuation_report = request.FILES.get('attachment')
#                 # files1 = {'files': (valuation_report.name, valuation_report, valuation_report.content_type)}
#                 # cleaned_data.pop('attachment', None)   
#                 # get Borrower Signature file
#                 borrower_signature = request.FILES.get('attachment1')
#                 # files2 = {'files': (borrower_signature.name, borrower_signature, borrower_signature.content_type)}
#                 # cleaned_data.pop('attachment1', None) 
                    
#                 if valuation_report:
#                     files['attachment'] =  (valuation_report.name, valuation_report, valuation_report.content_type)
#                 if borrower_signature:
#                     files['attachment1'] = (borrower_signature.name, borrower_signature, borrower_signature.content_type)

#                 # Clean the data by removing attachment fields
#                 cleaned_data.pop('attachment', None)   
#                 cleaned_data.pop('attachment1', None) 
#                 data = {'ms_id':MSID, 'ms_payload':json.dumps(cleaned_data)}
#                 json_data = json.dumps(data)
#                 response = call_post_method_with_token_v2(BASEURL,ENDPOINT,data,token,files)
#                 if response['status_code'] ==  0:                  
#                     messages.info(request, "Well Done..! Application Submitted..")
#                     return redirect('collaterals')
#                 else:
#                     messages.info(request, "Oops..! Application Failed to Submitted..")
#             else:
#                 print('errorss',form.errors) 
#         context = {'form':form,'records':master_view,"save":True }
#         return render(request, 'collateral_management/collaterals.html',context)
#     except Exception as error:
#         return render(request, "error.html", {"error": error})    

# this function for disply loan application for view collateral and related documents
def collaterals_view(request):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')

        # getting application data
        MSID = get_service_plan('view loanapplication') # view_loanapplication
        if MSID is None:
            print('MISID not found') 
        payload_form = {'company_id':company_id}
        data = {'ms_id':MSID,'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})

        application_data = [data for data in response['data'] if data['is_active'] == True]
        context = {'records':application_data}
        return render(request,'collateral_management/loan_details1.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def collateral_details(request,pk): # pk is a loan application id 
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')

        # getting company wise loan applications
        MSID = get_service_plan('view loanapplication') # view_loanapplication
        if MSID is None:
            print('MSID not found')
        data = {'ms_id': MSID,'ms_payload': {'loanapplication_id':pk}}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        if response['status_code'] == 1:
            return render(request,"error.html", {"error": response['data']})
        # Check if the response contains data
        if 'data' in response:
            loanapp_id_records = response['data'][0]
        else:
            print('Data not found in response')
        
        # getting loan application collaterals
        MSID = get_service_plan('view collaterals') # view_collaterals
        if MSID is None:
            print('MSID not found')
        data = {'ms_id': MSID,'ms_payload': {'company_id':company_id,'loan_appliaction_id':pk}}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        if response['status_code'] == 1:
            return render(request,"error.html", {"error": response['data']})
        # Check if the response contains data
        if 'data' in response:
            collateral_records = response['data']
        else:
            print('Data not found in response')
        
        # getting loan applcation document 
        MSID = get_service_plan('view collateraldocument') # view_collateraldocument
        if MSID is None:
            print('MSID not found')
        data = {'ms_id': MSID,'ms_payload': {'loan_application_id':pk}}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        if response['status_code'] == 1:
            return render(request,"error.html", {"error": response['data']})
        # Check if the response contains data
        if 'data' in response:
            collateraldoc_records = response['data']
        else:
            print('Data not found in response')

        context = {
            'loanapplication_records':loanapp_id_records,'collateral_records':collateral_records,'BASEURL':BASEURL,'collateraldoc_records':collateraldoc_records
        }
        return render(request, 'collateral_management/collateral_details.html', context)
    except Exception as error:
        return render(request, "error.html", {"error": error}) 
    

def collaterals_edit(request,pk):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        MSID = get_service_plan('view company')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            company_records = response['data']
        else:
            print('Data not found in response')
       
        MSID = get_service_plan('view loanapplication')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            loanapp_id_records = response['data']
        else:
            print('Data not found in response')
       
        MSID = get_service_plan('view customer')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            customer_id_records = response['data']
        else:
            print('Data not found in response')
       
        MSID = get_service_plan('view collateraltype')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            collateral_type_records = response['data']
        else:
            print('Data not found in response')
        MSID= get_service_plan('view collaterals')
        if MSID is None:
            print('MISID not found')
        payload_form = {
            "collaterals_id":pk
        }    
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        print('data',response['data'])
        master_type_edit = response['data'][0]
        
        form = CollateralsForm(initial=master_type_edit,company_choice=company_records,loanapp_id_choice=loanapp_id_records,customer_id_choice=customer_id_records,collateral_type_choice=collateral_type_records)

        MSID= get_service_plan('view collaterals')
        if MSID is None:
                print('MISID not found')
        payload_form = {       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']
        print('master_view',master_view)

        if request.method == 'POST':
            MSID= get_service_plan('update collaterals')
            if MSID is None:
                print('MISID not found')
            form = CollateralsForm(request.POST,company_choice=company_records,loanapp_id_choice=loanapp_id_records,customer_id_choice=customer_id_records,collateral_type_choice=collateral_type_records)
            if form.is_valid():
                cleaned_data = form.cleaned_data          
                cleaned_data['collaterals_id'] = pk    
                cleaned_data['valuation_date'] = cleaned_data['valuation_date'].strftime('%Y-%m-%d')
                   
                data={
                    'ms_id':MSID,
                    'ms_payload':cleaned_data
                }
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                if response['status_code'] == 0:
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('/collaterals')
                else:
                    # return JsonResponse({'error': 'Failed to save form data'}, status=400)
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 

        context={   
            "collaterals_view_active":"active",
            "form":form,
            "edit":True,
            "records":master_view
        }
        return render(request, 'collaterals_edit.html',context)   
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def collaterals_delete(request,pk):
    try:
        token = request.session['user_token']
        MSID= get_service_plan('delete collaterals')
        if MSID is None:
            print('MISID not found') 
        payload_form = {
            "collaterals_id":pk       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 0:
            
            messages.info(request, "Well Done..! Application Submitted..")
            return redirect('collaterals')
        else:
            messages.info(request, "Oops..! Application Failed to Submitted..")
    except Exception as error:
        return render(request, "error.html", {"error": error}) 

# ======================== repayment schedule ====================

def disbursed_loans(request):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')

        # getting loans
        MSID = get_service_plan('view loan') # view_loan
        if MSID is None:
            print('MISID not found') 
        payload_form = {'company':company_id}
        data = {'ms_id':MSID,'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,"error.html", {"error": response['data']})
        
        active_loan  = [data for data in response['data'] if data['is_active'] == True and data['workflow_stats'] == 'Disbursment']
        
        context = {'records':active_loan}
        return render(request,'repayment_schedule/disbursed_loans.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error}) 

def repayment_schedule(request,pk): # pk = loan id
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')

         # getting loans
        MSID = get_service_plan('view loan') # view_loan
        if MSID is None:
            print('MISID not found') 
        payload_form = {'loan_id':pk}
        data = {'ms_id':MSID,'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,"error.html", {"error": response['data']})
        loan_data = response['data'][0]

        MSID = get_service_plan('getting repayment schedules') # getting_repayment_schedules
        if MSID is None:
            print('MISID not found') 
        payload_form = {'company_id':company_id,'loanapp_id':pk}
        data = {'ms_id':MSID,'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,"error.html", {"error": response['data']})
        schedules = response['data']
        # calculate Total amount Due
        
        total_installment_amount = sum(item['instalment_amount'] for item in schedules)
        total_paid_amount = sum(item['paid_amount'] for item in schedules)
        if request.method == 'POST':
            MSID = get_service_plan('confirmed schedule') # confirmed_schedule
            if MSID is None:
                print('MISID not found') 
            payload_form = {'loan_id':pk}
            data = {'ms_id':MSID,'ms_payload':payload_form}
            json_data = json.dumps(data)
            response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
            if response['status_code'] == 1:
                return render(request,"error.html", {"error": response['data']})
            return redirect('disbursed_loans')

        context = {'schedules':response['data'],'loan_data':loan_data,'total_installment_amount':total_installment_amount,'total_paid_amount':total_paid_amount}
        return render(request,'repayment_schedule/repayment_schedule.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error}) 



def disbursedloans_foroverview(request):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')

        # getting loans
        MSID = get_service_plan('view loan') # view_loan
        if MSID is None:
            print('MISID not found') 
        payload_form = {'company':company_id}
        data = {'ms_id':MSID,'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,"error.html", {"error": response['data']})
        
        active_loan  = [data for data in response['data'] if data['is_active'] == True and data['workflow_stats'] == 'Disbursment']
        
        context = {'records':active_loan}
        return render(request,'repayment_schedule/disbursedloans_overview.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error}) 

def schedule_overview(request,pk):  # pk = loan id
    try:
        context = {}
        return render(request,'repayment_schedule/schedule_overview.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error}) 



#---------------------------------------repayment 2 ----------------------------


def disbursed_loans1(request):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')

        # getting loans
        MSID = get_service_plan('view loan') # view_loan
        if MSID is None:
            print('MISID not found') 
        payload_form = {'company':company_id}
        data = {'ms_id':MSID,'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,"error.html", {"error": response['data']})
        
        active_loan  = [data for data in response['data'] if data['is_active'] == True and data['workflow_stats'] == 'Disbursment']
        
        context = {'records':active_loan}
        return render(request,'repayment_schedule1/disbursed_loans1.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error}) 


def repayment_schedule1(request,pk): # pk = loan id
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')

         # getting loans
        MSID = get_service_plan('view loan') # view_loan
        if MSID is None:
            print('MISID not found') 
        payload_form = {'loan_id':pk}
        data = {'ms_id':MSID,'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,"error.html", {"error": response['data']})
        loan_data = response['data'][0]

        MSID = get_service_plan('getting repayment schedules') # getting_repayment_schedules
        if MSID is None:
            print('MISID not found') 
        payload_form = {'company_id':company_id,'loanapp_id':pk}
        data = {'ms_id':MSID,'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,"error.html", {"error": response['data']})
        schedules = response['data']
        # calculate Total amount Due
        
        total_installment_amount = sum(item['instalment_amount'] for item in schedules)
        total_paid_amount = sum(item['paid_amount'] for item in schedules)
        
        # next payments
        
        if request.method == 'POST':
            MSID = get_service_plan('confirmed schedule') # confirmed_schedule
            if MSID is None:
                print('MISID not found') 
            payload_form = {'loan_id':pk}
            data = {'ms_id':MSID,'ms_payload':payload_form}
            json_data = json.dumps(data)
            response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
            if response['status_code'] == 1:
                return render(request,"error.html", {"error": response['data']})
            return redirect('disbursed_loans')

        context = {'schedules':response['data'],'loan_data':loan_data,'total_installment_amount':total_installment_amount,'total_paid_amount':total_paid_amount}
        return render(request,'repayment_schedule1/repayment_schedule1.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error}) 


def disbursedloans_foroverview1(request):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')

        # getting loans
        MSID = get_service_plan('view loan') # view_loan
        if MSID is None:
            print('MISID not found') 
        payload_form = {'company':company_id}
        data = {'ms_id':MSID,'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,"error.html", {"error": response['data']})
        
        active_loan  = [data for data in response['data'] if data['is_active'] == True and data['workflow_stats'] == 'Disbursment']
        
        context = {'records':active_loan}
        return render(request,'repayment_schedule1/disbursedloans_overview1.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error}) 

def schedule_overview1(request,pk):  # pk = loan id
    try:
        context = {}
        return render(request,'repayment_schedule1/schedule_overview1.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error}) 


def payment_process(request,schedule_id):
    try:
        token = request.session['user_token'] 
        company_id = request.session.get('company_id') 
        MSID = get_service_plan('getting schedule') # getting_schedules
        if MSID is None:
            print('MISID not found') 
        payload_form = {'schedule_id':schedule_id}
        data = {'ms_id':MSID,'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,"error.html", {"error": response['data']})
        schedule = response['data']
        print('schedule',schedule)


        if request.method == 'POST':
            MSID = get_service_plan('paid schedule') # paid
            if MSID is None:
                print('MISID not found') 
            payload_form = {'schedule_id':schedule_id}
            data = {'ms_id':MSID,'ms_payload':payload_form}
            json_data = json.dumps(data)
            response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
            if response['status_code'] == 1:
                return render(request,"error.html", {"error": response['data']})
            return redirect('disbursed_loans1')

        context= {'schedule':response['data']}
        return render(request,'repayment_schedule1/payment_process.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error}) 
        



#=============== Loan Calculater ====================

# ==================== Loan Calculater ===================================
def loancalculators_create(request):
    try:
        token = request.session['user_token']
        form = LoancalculatorsForm()
        response = {"data":None}
        if request.method == "POST":
            form = LoancalculatorsForm(request.POST)
            if form.is_valid():
                MSID = get_service_plan('calculate repayment schedule')
                if MSID is None:
                    print('MISID not found')      
                cleaned_data = form.cleaned_data
          
                cleaned_data['repayment_start_date'] = cleaned_data['repayment_start_date'].strftime('%Y-%m-%d')  
                data = {'ms_id':MSID,'ms_payload':cleaned_data} 
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                if response['status_code'] == 1:
                    return render(request,'error.html',{'error':str(response['data'])})
                
                total_payments = sum(item['Installment'] for item in response['data'])
                total_interest = sum(item['Interest'] for item in response['data'])
          
                context = {'form':form,"save":True,'records':response['data'],'total_payments':total_payments,'total_interest':total_interest}
                return render(request, 'loan_calculator/loancalculators.html',context)
            else:
                print('errorss',form.errors) 
        context = {'form':form,"save":True,'records':response['data']}
        return render(request, 'loan_calculator/loancalculators.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})  



# ==================================== Settings  functions ======================
# customer document list or customer identification type master
def identificationtype_create(request):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        form = IdentificationtypeForm()
        
        if request.method == "POST":
            form = IdentificationtypeForm(request.POST)
            if form.is_valid():
                MSID = get_service_plan('create identificationtype') # create_identificationtype
                if MSID is None:
                    print('MISID not found')      
                cleaned_data = form.cleaned_data
                cleaned_data['company_id'] = company_id
                data = {'ms_id':MSID,'ms_payload':cleaned_data} 
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                print("response",response)
                if response['status_code'] ==  0:                  
                    messages.info(request, "Well Done..! Application Submitted..")
                    
                else:
                    messages.info(request, "Oops..! Application Failed to Submitted..")
                return redirect('identificationtype')
            else:
                print('errorss',form.errors) 

        context = { 'form':form,"save":True }
        return render(request, 'Settings/identificationtype.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def identificationtype_view(request):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        MSID = get_service_plan('view identificationtype') # view_identificationtype
        if MSID is None:
            print('MISID not found')
        payload_form = {'company_id':company_id}    
        data = {'ms_id':MSID,'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        master_view = response['data']
  
        context = {   
            "identificationtype_view_active":"active",
            "records":master_view,
            "View":True
        }
        return render(request, 'Settings/identificationtype_view.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def identificationtype_edit(request,pk):
    try:
        token = request.session['user_token']
       
        company_id = request.session.get('company_id')

        MSID = get_service_plan('view identificationtype') # view identificationtype
        if MSID is None:
            print('MISID not found')
        payload_form = {
            "identificationtype_id":pk
        }    
        data = {'ms_id':MSID,'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        print('data',response['data'])
        master_type_edit = response['data'][0]
        
        form = IdentificationtypeForm(initial=master_type_edit)

        if request.method == 'POST':
            MSID= get_service_plan('update identificationtype') # update_identificationtype
            if MSID is None:
                print('MISID not found')
            form = IdentificationtypeForm(request.POST)
            if form.is_valid():
                cleaned_data = form.cleaned_data          
                cleaned_data['identificationtype_id'] = pk    
        
                data = {'ms_id':MSID,'ms_payload':cleaned_data}
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                if response['status_code'] == 0:
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('/identificationtype')
                else:
                    # return JsonResponse({'error': 'Failed to save form data'}, status=400)
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 

        context={   
            "identificationtype_view_active":"active",
            "form":form,
            "edit":True,}
        return render(request, 'Settings/identificationtype.html',context)   
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def identificationtype_delete(request,pk):
    try:
        token = request.session['user_token']
        MSID = get_service_plan('delete identificationtype')
        if MSID is None:
            print('MISID not found') 
        payload_form = {"identificationtype_id":pk}
        data = {'ms_id':MSID,'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 0:
            messages.info(request, "Well Done..! Application Submitted..")
            return redirect('identificationtype')
        else:
            messages.info(request, "Oops..! Application Failed to Submitted..")
    except Exception as error:
        return render(request, "error.html", {"error": error}) 

# back account master

def bankaccount_create(request):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        form = BankaccountForm()

        if request.method == "POST":
            form = BankaccountForm(request.POST)
            if form.is_valid():
                MSID = get_service_plan('create bank account')
                if MSID is None:
                    print('MISID not found')      
                cleaned_data = form.cleaned_data
                cleaned_data ['company_id'] = company_id
                data={'ms_id':MSID,'ms_payload':cleaned_data} 
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                if response['status_code'] ==  0:                  
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('bankaccount')
                else:
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 
        
        context = { 'form':form,"save":True}
        return render(request, 'Settings/bankaccount.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def bankaccount_view(request):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        MSID = get_service_plan('view bank account')
        if MSID is None:
            print('MISID not found')
        payload_form = {'company_id':company_id}
        data={'ms_id':MSID,'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        master_view = response['data']

        context={   
            "bankaccount_view_active":"active",
            "records":master_view,
            "View":True
        }
        return render(request, 'Settings/bankaccount_view.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def bankaccount_edit(request,pk):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        
        MSID = get_service_plan('view bank account')
        if MSID is None:
            print('MISID not found')
        payload_form = {"account_number":pk}    
        data = {'ms_id':MSID,'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        master_type_edit = response['data'][0]
 
        form = BankaccountForm(initial=master_type_edit)

        if request.method == 'POST':
            MSID= get_service_plan('update bank account')
            if MSID is None:
                print('MISID not found')
            form = BankaccountForm(request.POST)
            if form.is_valid():
                cleaned_data = form.cleaned_data          
                cleaned_data['bank_id'] = pk    
                cleaned_data['company_id'] = company_id
                data = {'ms_id':MSID,'ms_payload':cleaned_data}
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                if response['status_code'] == 0:
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('bankaccount')
                else:
                    # return JsonResponse({'error': 'Failed to save form data'}, status=400)
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 

        context={   
            "bankaccount_view_active":"active",
            "form":form,
            "edit":True,
        }
        return render(request, 'Settings/bankaccount.html',context)   
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def bankaccount_delete(request,pk):
    try:
        token = request.session['user_token']
        MSID = get_service_plan('delete bank account')
        if MSID is None:
            print('MISID not found') 
        payload_form = {"back_id":pk}
        data = {'ms_id':MSID,'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 0:
            messages.info(request, "Well Done..! Your Back Account Deleted..")
            return redirect('bankaccount')
        else:
            messages.info(request, "Oops..! Application Failed to Submitted..")
        return redirect('bankaccount')
    except Exception as error:
        return render(request, "error.html", {"error": error}) 

# currency master
def currency_create(request):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        
        form = CurrencyForm()
        if request.method == "POST":
            form = CurrencyForm(request.POST)
            if form.is_valid():
                MSID = get_service_plan('create currency')
                if MSID is None:
                    print('MISID not found')      
                cleaned_data = form.cleaned_data  
                cleaned_data['company_id'] = company_id
                data = {'ms_id':MSID, 'ms_payload':cleaned_data} 
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                print('response',response)
                if response['status_code'] ==  0:                  
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('currency')
                else:
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 
        
        context = {'form':form,"save":True}
        return render(request, 'Settings/currency.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def currency_view(request):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
      
        MSID = get_service_plan('view currency')
        if MSID is None:
            print('MISID not found')
        payload_form = {'company_id':company_id }
        data = {
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        master_view = response['data']
        context={   
            "currency_view_active":"active",
            "records":master_view,
            "View":True
        }
        return render(request, 'Settings/currency_view.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def currency_edit(request,pk):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        
        MSID = get_service_plan('view currency')
        if MSID is None:
            print('MISID not found')
        payload_form = {
            "currency_id":pk
        }    
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        master_type_edit = response['data'][0]
        
        form = CurrencyForm(initial=master_type_edit)

        if request.method == 'POST':
            MSID= get_service_plan('update currency')
            if MSID is None:
                print('MISID not found')
            form = CurrencyForm(request.POST)
            if form.is_valid():
                cleaned_data = form.cleaned_data  
                cleaned_data['company_id'] = company_id  
                cleaned_data['currency_id'] = pk    
                   
                data = {
                    'ms_id':MSID,
                    'ms_payload':cleaned_data
                }
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                if response['status_code'] == 0:
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('currency')
                else:
                    # return JsonResponse({'error': 'Failed to save form data'}, status=400)
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 

        context={   
            "currency_view_active":"active",
            "form":form,
            "edit":True,
        }
        return render(request, 'Settings/currency.html',context)   
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def currency_delete(request,pk):
    try:
        token = request.session['user_token']
        MSID= get_service_plan('delete currency')
        if MSID is None:
            print('MISID not found') 
        payload_form = {
            "currency_id":pk       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 0:
            
            messages.info(request, "Well Done..! Application Submitted..")
            return redirect('currency')
        else:
            messages.info(request, "Oops..! Application Failed to Submitted..")
    except Exception as error:
        return render(request, "error.html", {"error": error}) 

# payment method

def paymentmethod_create(request):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        form = PaymentmethodForm()
        if request.method == "POST":
            form = PaymentmethodForm(request.POST)
            if form.is_valid():
                MSID = get_service_plan('create paymentmethod') # create paymentmethod
                if MSID is None:
                    print('MISID not found')      
                cleaned_data = form.cleaned_data
                cleaned_data['company_id'] = company_id    
                data = {'ms_id':MSID,'ms_payload':cleaned_data} 
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                print('response',response)
                if response['status_code'] ==  0:                  
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('paymentmethod')
                else:
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 
        
        context = {       
            'form':form,"save":True
        }
        return render(request, 'Settings/paymentmethod.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def paymentmethod_view(request):
    try:
        token = request.session['user_token'] 
        company_id = request.session.get('company_id') 
        MSID= get_service_plan('view paymentmethod')
        if MSID is None:
            print('MISID not found')
        payload_form = {'company_id':company_id}
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        master_view = response['data']
        context={   
            "paymentmethod_view_active":"active",
            "records":master_view,
            "View":True
        }
        return render(request, 'Settings/paymentmethod_view.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def paymentmethod_edit(request,pk):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        MSID = get_service_plan('view paymentmethod')
        if MSID is None:
            print('MISID not found')
        payload_form = {
            "paymentmethod_id":pk
        }    
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        master_type_edit = response['data'][0]
        
        form = PaymentmethodForm(initial=master_type_edit)

        if request.method == 'POST':
            MSID= get_service_plan('update paymentmethod')
            if MSID is None:
                print('MISID not found')
            form = PaymentmethodForm(request.POST)
            if form.is_valid():
                cleaned_data = form.cleaned_data          
                cleaned_data['paymentmethod_id'] = pk    
                cleaned_data['company_id'] = company_id
                   
                data={
                    'ms_id':MSID,
                    'ms_payload':cleaned_data
                }
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                if response['status_code'] == 0:
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('paymentmethod')
                else:
                    # return JsonResponse({'error': 'Failed to save form data'}, status=400)
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 
        context = {   
            "paymentmethod_view_active":"active",
            "form":form,
            "edit":True,
        }
        return render(request, 'Settings/paymentmethod.html',context)   
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def paymentmethod_delete(request,pk):
    try:
        token = request.session['user_token']
        MSID= get_service_plan('delete paymentmethod')
        if MSID is None:
            print('MISID not found') 
        payload_form = {
            "paymentmethod_id":pk       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 0:
            
            messages.info(request, "Well Done..! Application Submitted..")
            return redirect('paymentmethod')
        else:
            messages.info(request, "Oops..! Application Failed to Submitted..")
    except Exception as error:
        return render(request, "error.html", {"error": error}) 

# collateral Type
def collateraltype_create(request):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        form = CollateraltypeForm()
        if request.method == "POST":
            form = CollateraltypeForm(request.POST)
            if form.is_valid():
                MSID = get_service_plan('create collateraltype')
                if MSID is None:
                    print('MISID not found')      
                cleaned_data = form.cleaned_data
                cleaned_data['company_id'] = company_id
                data = {
                    'ms_id':MSID,
                    'ms_payload':cleaned_data
                } 
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                if response['status_code'] ==  0:                  
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('collateraltype')
                else:
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 
        
        context = {      
            'form':form,"save":True
        }
        return render(request, 'Settings/collateraltype.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def collateraltype_view(request):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')  
        MSID = get_service_plan('view collateraltype')
        if MSID is None:
            print('MISID not found')
        payload_form = {'company_id':company_id}
        data =  {
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        master_view = response['data']
        context = {   
            "collateraltype_view_active":"active",
            "records":master_view,
            "View":True
        }
        return render(request, 'Settings/collateraltype_view.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def collateraltype_edit(request,pk):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')

        MSID = get_service_plan('view collateraltype')
        if MSID is None:
            print('MISID not found')
        payload_form = {
            "collateraltype_id":pk
        }    
        data = {
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        print('data',response['data'])
        master_type_edit = response['data'][0]
        
        form = CollateraltypeForm(initial=master_type_edit)

        if request.method == 'POST':
            MSID= get_service_plan('update collateraltype')
            if MSID is None:
                print('MISID not found')
            form = CollateraltypeForm(request.POST)
            if form.is_valid():
                cleaned_data = form.cleaned_data          
                cleaned_data['collateraltype_id'] = pk    
                cleaned_data['company_id'] = company_id
                   
                data={
                    'ms_id':MSID,
                    'ms_payload':cleaned_data
                }
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                if response['status_code'] == 0:
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('collateraltype')
                else:
                    # return JsonResponse({'error': 'Failed to save form data'}, status=400)
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 

        context={   
            "collateraltype_view_active":"active",
            "form":form,
            "edit":True,
        }
        return render(request, 'Settings/collateraltype.html',context)   
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def collateraltype_delete(request,pk):
    try:
        token = request.session['user_token']
        MSID = get_service_plan('delete collateraltype')
        if MSID is None:
            print('MISID not found') 
        payload_form = {
            "collateraltype_id":pk       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 0:
            
            messages.info(request, "Well Done..! Application Submitted..")
            return redirect('collateraltype')
        else:
            messages.info(request, "Oops..! Application Failed to Submitted..")
    except Exception as error:
        return render(request, "error.html", {"error": error}) 
    
# loan type
  
def loantype_create(request):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        form = LoantypeForm()
      
        if request.method == "POST":
            form = LoantypeForm(request.POST)
            if form.is_valid():
                MSID= get_service_plan('create loantype') # create_loantype
                if MSID is None:
                    print('MISID not found')      
                cleaned_data = form.cleaned_data   
                cleaned_data['company_id'] = company_id
                data = {'ms_id':MSID,'ms_payload':cleaned_data} 
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                if response['status_code'] ==  0:                  
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('loantype')
                else:
                    messages.info(request, str(response['data']))
       
            else:
                print('errorss',form.errors) 
                messages.info(request, str(form.errors))
        
        context = {      
            'form':form,"save":True
        }
        return render(request, 'Settings/loantype.html',context)
    except Exception as error:
        print('=============')
        return render(request, "error.html", {"error": error})    

def loantype_view(request):
    try:
        token = request.session['user_token'] 
        company_id = request.session.get('company_id')
        MSID = get_service_plan('view loantype') # view_loantype
        if MSID is None:
            print('MISID not found')
        payload_form = {'company_id':company_id }
        data = {'ms_id':MSID,'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        master_view = response['data']

        context={   
            "loantype_view_active":"active",
            "records":master_view,
            "View":True
        }
        return render(request, 'Settings/loantype_view.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def loantype_edit(request,pk):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        MSID = get_service_plan('view loantype')
        if MSID is None:
            print('MISID not found')
        payload_form = { "loantype_id":pk}    
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
      
        master_type_edit = response['data'][0]
        
        form = LoantypeForm(initial=master_type_edit)

        if request.method == 'POST':
            MSID= get_service_plan('update loantype')
            if MSID is None:
                print('MISID not found')
            form = LoantypeForm(request.POST)
            if form.is_valid():
                cleaned_data = form.cleaned_data          
                cleaned_data['loantype_id'] = pk    
                cleaned_data['company_id'] = company_id
                data={
                    'ms_id':MSID,
                    'ms_payload':cleaned_data
                }
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                if response['status_code'] == 0:
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('loantype')
                else:
                    # return JsonResponse({'error': 'Failed to save form data'}, status=400)
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 

        context={   
            "loantype_view_active":"active",
            "form":form,
            "edit":True,
        }
        return render(request, 'Settings/loantype.html',context)   
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def loantype_delete(request,pk):
    try:
        token = request.session['user_token']
        MSID= get_service_plan('delete loantype')
        if MSID is None:
            print('MISID not found') 
        payload_form = {"loantype_id":pk}
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 0:
            messages.info(request, "Well Done..! Application Submitted..")
            return redirect('/loantype')
        else:
            messages.info(request, "Oops..! Application Failed to Submitted..")
    except Exception as error:
        return render(request, "error.html", {"error": error}) 


def aggrement_template_create(request):
    try:
        token = request.session['user_token']
        template_form = TemplateForm()
        help_text = '''
        {{cutomer_first_name}},{{cutomer_lastname}},{{cutomer_email}},{{cutomer_age}},{{cutomer_phone_number}},{{cutomer_address}},{{dateofbirth}}
        {{application_id}},{{loan_type}},{{loan_amount}},{{loan_purpose}},{{approved_amount}},{{interest_rate}},{{tenure}},{{tenure_type}},{{repayment_schedule}},{{repayment_mode}},
        {{interest_basics}},{{loan_calculation_method}},

        '''
        if request.method == 'POST':
            template_name = request.POST.get('template_name')
            content = request.POST.get('content')
            MSID= get_service_plan('template create')
            if MSID is None:
                print('MISID not found') 
            payload_form = {"template_name":template_name,'content':content}
            data={
                'ms_id':MSID,
                'ms_payload':payload_form
            }
            json_data = json.dumps(data)
            response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
            if response['status_code'] == 0:
                messages.info(request, "Well Done..! Application Submitted..")
                return redirect('/aggrement_template_list')
            else:
                messages.info(request, "Oops..! Application Failed to Submitted..")

        context={   
           'form':template_form,'help_text':help_text
        }
        return render(request, 'loan_agreement/aggrement_template_create.html',context)   
    except Exception as e:
        return render(request, "error.html", {"errors": e}) 


def aggrement_template_list(request):
    try:
        token = request.session['user_token']
        MSID= get_service_plan('view template')
        if MSID is None:
            print('MISID not found') 
        payload_form = {}
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 0:
            messages.info(request, "Well Done..! Application Submitted..")
        else:
            messages.info(request, "Oops..! Application Failed to Submitted..")

        records =  response.get('data')
        context={   
           'records':records,
        }
        return render(request, 'loan_agreement/aggrement_template_list.html',context)   
    except Exception as e:
        return render(request, "error.html", {"errors": e}) 


def aggrement_template_view(request,template_id):
    try:
        token = request.session['user_token']
        MSID= get_service_plan('view template')
        if MSID is None:
            print('MISID not found')
        payload_form = {"template_id":template_id}
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 0:
            messages.info(request, "Well Done..! Application Submitted..")
        else:
            messages.info(request, "Oops..! Application Failed to Submitted..")

        record = response.get('data')[0]
        print('record',record)
        template_form = TemplateForm(initial={'content':record.get('content')})
        help_text = '''
        {{cutomer_first_name}},{{cutomer_lastname}},{{cutomer_email}},{{cutomer_age}},{{cutomer_phone_number}},{{cutomer_address}},{{dateofbirth}}
        {{application_id}},{{loan_type}},{{loan_amount}},{{loan_purpose}},{{loan_type}},{{loan_type}}

        This content contains placeholders that will be replaced with specific values during the generation process. If additional placeholders are needed, create a new name for the tag, and we will ask for the corresponding value to include it in the final output.
        '''
     
        context={   
           'form':template_form,'help_text':help_text,'record':record,'view':True
        }
        return render(request, 'loan_agreement/aggrement_template_create.html',context)   
    except Exception as e:
        return render(request, "error.html", {"errors": e}) 

def audit_view(request):
    try:
        token = request.session['user_token']

        MSID = get_service_plan('user check')
        if MSID is None:
            print('MISID not found')
        payload_form = {}
        data = {'ms_id':MSID,'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        user_check=response['data'][0]
        print("responseuser_checkty7u8i",)


        if user_check == True:
            MSID = get_service_plan('view audit')
            if MSID is None:
                print('MISID not found')
            payload_form = {}
            data = {'ms_id':MSID,'ms_payload':payload_form}
            json_data = json.dumps(data)
            response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
            print("response",response)
            if response['status_code'] == 1:
                return render(request,'error.html',{'error':str(response['data'])})
            master_view = response['data']
            print("master_view4567890",master_view)
        else:
            master_view=None
            pass            
        context = {   
            "customer_view_active":"active",
            "records":master_view,
            "View":True
        }
        return render(request, 'audit_log.html',context)

    except Exception as error:
        return render(request, "error.html", {"error": error})    



def document_list(request):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')

        # getting all customer data 
        MSID = get_service_plan('view customer') # view_customer
        if MSID is None:
            print('MSID not found')
        data = {'ms_id': MSID,'ms_payload': {'company_id':company_id}}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        # Check if the response contains data
        if 'data' in response:
            customer_records = response['data']
        else:
            print('Data not found in response')

        return render(request,'customer_management/document_list.html',{'records':customer_records})
    except Exception as error:
        return render(request, "error.html", {"error": error}) 



def customer_document_view(request,pk): #pk = customer id
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')

        MSID = get_service_plan('getting verified ducuments') 
        if MSID is None:
            print('MISID not found') 
        payload_form = {"company_id":company_id,'customer_id':pk}
        data = {'ms_id':MSID,'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        
        customer_doc = response['data']
        context = {'documents':customer_doc,'BASEURL':BASEURL}

        return render(request,'customer_management/customer_document_view.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error}) 



def loan_upadate_trenches(request,loanapp_id):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        MSID = get_service_plan('create loanvaluechain') # create_loanvaluechain
        if MSID is None:
            print('MSID not found')
        payloads = {'company_id':company_id,'loanapp_id':loanapp_id}
        data = {'ms_id': MSID,'ms_payload': payloads}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        print('response',response)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        value_chain_data = response['data']
        print('value_chain_data',value_chain_data)
        return redirect('loan_list')
    except Exception as error:
        return render(request, "error.html", {"error": error}) 
    
def loan_detail_trenches(request,loanapp_id):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        MSID = get_service_plan('loan detail value chain get') # getting_valuechainsetups
        if MSID is None:
            print('MSID not found')
        payloads = {'loanapp_id':loanapp_id}
        data = {'ms_id': MSID,'ms_payload': payloads}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        records = response['data']
        print('records',records)
        context = {
            'records':records,'loanapp_id':loanapp_id,
        }

        return render(request,'loan_detail_trenches.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error}) 
    

def milestone_edit_v1(request,loanapp_id):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        if request.method == 'POST':
            milestone_id = request.POST.get('milestone_id')
            amount = request.POST.get('amount')

            MSID = get_service_plan('milestone edit v1') # getting_valuechainsetups
            if MSID is None:
                print('MSID not found')
            payloads = {'milestone_id':milestone_id,'amount':amount}
            data = {'ms_id': MSID,'ms_payload': payloads}
            json_data = json.dumps(data)
            response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
            if response['status_code'] == 1:
                return render(request,'error.html',{'error':str(response['data'])})
            return redirect(f"/loan_detail_trenches/{loanapp_id}/")
       
    except Exception as error:
        return render(request, "error.html", {"error": error}) 
    

def milestone_activity_edit_v1(request,loanapp_id):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        if request.method == 'POST':
            activity_id = request.POST.get('activity_id')
            amount = request.POST.get('amount')

            MSID = get_service_plan('milestone activity edit v1') # getting_valuechainsetups
            if MSID is None:
                print('MSID not found')
            payloads = {'activity_id':activity_id,'amount':amount}
            data = {'ms_id': MSID,'ms_payload': payloads}
            json_data = json.dumps(data)
            response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
            if response['status_code'] == 1:
                return render(request,'error.html',{'error':str(response['data'])})
            return redirect(f"/loan_detail_trenches/{loanapp_id}/")
       
    except Exception as error:
        return render(request, "error.html", {"error": error}) 


def milestone_activity_delete_v1(request,loanapp_id,activity_id):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')

        MSID = get_service_plan('milestone activity delete v1') 
        if MSID is None:
            print('MSID not found')
        payloads = {'activity_id':activity_id}
        data = {'ms_id': MSID,'ms_payload': payloads}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        return redirect(f"/loan_detail_trenches/{loanapp_id}/")
       
    except Exception as error:
        return render(request, "error.html", {"error": error}) 


def milestone_delete_v1(request,loanapp_id,milestone_id):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')

        MSID = get_service_plan('milestone delete v1') 
        if MSID is None:
            print('MSID not found')
        payloads = {'milestone_id':milestone_id}
        data = {'ms_id': MSID,'ms_payload': payloads}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        return redirect(f"/loan_detail_trenches/{loanapp_id}/")
       
    except Exception as error:
        return render(request, "error.html", {"error": error}) 


def milestone_activity_create_v1(request,loanapp_id):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        if request.method == 'POST':
            milestone_id = request.POST.get('milestone_id')
            activity_name = request.POST.get('activity_name')
            description = request.POST.get('description')
            amount = request.POST.get('amount')

            MSID = get_service_plan('milestone activity create v1') # getting_valuechainsetups
            if MSID is None:
                print('MSID not found')
            payloads = {'milestone_id':milestone_id,'amount':amount,'activity_name':activity_name,'description':description}
            data = {'ms_id': MSID,'ms_payload': payloads}
            json_data = json.dumps(data)
            response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
            if response['status_code'] == 1:
                return render(request,'error.html',{'error':str(response['data'])})
            return redirect(f"/loan_detail_trenches/{loanapp_id}/")
       
    except Exception as error:
        return render(request, "error.html", {"error": error}) 
    

def milestone_create_v1(request,loanapp_id):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        if request.method == 'POST':
            valuechain_id = request.POST.get('valuechain_id')
            milestone_name = request.POST.get('milestone_name')
            description = request.POST.get('description')
            amount = request.POST.get('amount')
            due_date = request.POST.get('due_date')

            MSID = get_service_plan('milestone create v1') # getting_valuechainsetups
            if MSID is None:
                print('MSID not found')
            payloads = {'valuechain_id':valuechain_id,'amount':amount,'milestone_name':milestone_name,'description':description,'due_date':due_date}
            data = {'ms_id': MSID,'ms_payload': payloads}
            json_data = json.dumps(data)
            response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
            if response['status_code'] == 1:
                return render(request,'error.html',{'error':str(response['data'])})
            return redirect(f"/loan_detail_trenches/{loanapp_id}/")
       
    except Exception as error:
        return render(request, "error.html", {"error": error}) 

#=================== Penalty ==========================

def disply_penaltyloans(request):
    try:
        
        return render(request,"Penalties/disply_penaltyloans.html")
    except Exception as error:
        return render(request, "error.html", {"error": error}) 


def milestone_disbursement(request,loan_id):
    # try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        
        
        MSID = get_service_plan('loan detail value chain get') # getting_valuechainsetups
        if MSID is None:
            print('MSID not found')
        payloads = {'loanapp_id':loan_id}
        data = {'ms_id': MSID,'ms_payload': payloads}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        records = response['data']
        print('records',records)

          # getting related loan data
        MSID = get_service_plan('view loan') # view_loan
        if MSID is None:
            print('MSID not found')
        data = {'ms_id': MSID,'ms_payload': {'loan_id':loan_id}}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        loan_data = response['data'][0]
       

        #  getting customeraccount
        MSID = get_service_plan('getting customeraccount') # getting_customeraccount
        if MSID is None:
            print('MSID not found')
        data = {'ms_id': MSID,'ms_payload': {'customer_id':loan_data['customer']['id']}}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        borroweraccount = response['data'][0]

        if request.method == "POST":
            MSID = get_service_plan('create disbursement') # create_disbursement
            if MSID is None:
                print('MISID not found')      
            payloads = {'company_id':company_id,'customer_id':loan_data['customer']['id'],'loan_id':loan_data['id'], 'loan_application_id':loan_data['loanapp_id']['id'], 'amount':request.POST.get('disursement_amount'), 'disbursement_type':loan_data['loanapp_id']['disbursement_type'], 'disbursement_status':request.POST.get('disbursement_status'),'bank':borroweraccount['id']}
            data = {'ms_id':MSID,'ms_payload':payloads} 
            json_data = json.dumps(data)
            response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
            if response['status_code'] ==  0:                  
                messages.info(request, "Well Done..! Application Submitted..")

            MSID = get_service_plan('milestone compelete') # create_disbursement
            milestone_id = request.POST.get('milestone_id')
            if MSID is None:
                print('MISID not found')      
            payloads = {'milestone_id':milestone_id}
            data = {'ms_id':MSID,'ms_payload':payloads} 
            json_data = json.dumps(data)
            response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
            if response['status_code'] ==  0:                  
                messages.info(request, "Well Done..! Application Submitted..")
            return redirect("disply_loans")
        
        
        context = {
            'records':records,'loan_id':loan_id,'borroweraccount':borroweraccount
        }
        return render(request,'disbursement/milestone_disbursement.html',context)
    # except Exception as error:
    #     return render(request, "error.html", {"error": error})