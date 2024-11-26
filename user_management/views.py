from django.http import HttpResponse
from django.shortcuts import render, redirect,get_object_or_404
from mainapp.models import MS_ServicePlan
from .forms import *
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout
import json
from django.contrib import messages
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
import requests
from django.conf import settings



BASEURL = 'http://127.0.0.1:9000/'
# BASEURL = settings.BASEURL
ENDPOINT = 'micro-service/'




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

def call_post_method_without_token_forgot(URL, data):
    api_url = URL
    headers = {"Content-Type": "application/json"}  # No token included
    try:
        response = requests.post(api_url, json=data, headers=headers)
        if response.status_code in [200, 201]:
            print("Response if condition", response.status_code)
            return {'status_code': 0, 'data': response.json()}
        else:
            print("Response status code", response.status_code)
            return {'status_code': 1, 'data': response.json()}
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return {'status_code': 1, 'data': 'Something went wrong'}



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



def user_registration(request):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        MSID= get_service_plan('userprofile list')
        if MSID is None:
            print('MISID not found') 
        payload_form={

        }     
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        } 
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
    
        if response['status_code'] ==  1:                  
            messages.info(request, "Well Done..! Application Submitted..")
            print('error',response['data'])
        userprofile=response['data']
        if request.method == 'POST':
            form = UserRegistrationForm(request.POST)
            if form.is_valid():

                MSID= get_service_plan('user registration')
                print('MSID',MSID)
                if MSID is None:
                    print('MISID not found')      
                cleaned_data = form.cleaned_data
        
                data={
                    'ms_id':MSID,
                    'ms_payload':cleaned_data
                } 
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                
                if response['status_code'] ==  0:                  
                    messages.info(request, "Successfully created User")
                    return redirect('user_list')
                else:
                    context = {
                        'form': form, 'user_registration': 'active', 'user_registration_show': 'show','userprofile':userprofile,"error": response['data']
                    }
                    return render(request, 'UserManagement/user_registration.html', context)
        else:
            form = UserRegistrationForm()

        context = {
            'form': form, 'user_registration': 'active', 'user_registration_show': 'show','userprofile':userprofile
        }
        return render(request, 'UserManagement/user_registration.html', context)
    except Exception as error:
        return render(request, "error.html", {"error": error})   


# def user_login(request):
#     if request.method == 'POST':
#         print('request.POST', request.POST)
#         form = LoginForm(request.POST)
#         if form.is_valid():
#             email = form.cleaned_data.get('email')
#             password = form.cleaned_data.get('password')
#             user = authenticate(request, email=email, password=password)
#             if user is not None:
#                 login(request, user)
#                 return redirect('dashboard')  # Redirect to a success page
#             else:
#                 print('Invalid username or password')
#                 form.add_error(None, 'Invalid username or password')
#         else:
#             print('form', form.errors)
#     else:
#         form = LoginForm()

#     context = {
#         'form': form
#     }
#     return render(request, 'Auth/login.html', context)

def user_list(request):
    try:
        token = request.session['user_token']

        MSID= get_service_plan('get user')
        if MSID is None:
            print('MISID not found') 
        payload_form={

        }     
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        } 
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
    
        if response['status_code'] ==  0:                  
            messages.info(request, "Well Done..! Application Submitted..")
            records=response['data']
            
        #records = User.objects.all()
            context = {
                'user_list': 'active', 'user_list_show': 'show', 'records': records
            }
            return render(request, 'UserManagement/user_list.html', context)
    except Exception as error:
        return render(request, "error.html", {"error": error})   


def user_edit(request,pk):
    try:
        token = request.session['user_token']
        MSID= get_service_plan('userprofile list')
        if MSID is None:
            print('MISID not found') 
        payload_form={

        }     
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        } 
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
    
        if response['status_code'] ==  0:                  
            messages.info(request, "Well Done..! Application Submitted..")
            print('error',response['data'])
        user_profile=response['data']
        

        MSID= get_service_plan('get user')
        if MSID is None:
            print('MISID not found') 
        payload_form={
            'id':pk
        }     
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        } 
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
    

        record=response['data'][0]
        if request.method == 'POST':
            form = UserRegistrationForm(request.POST,initial=record)
            if form.is_valid():    
                MSID= get_service_plan('user edit')
                print('MSID',MSID)
                if MSID is None:
                    print('MISID not found')      
                cleaned_data = form.cleaned_data
                cleaned_data['id']=pk
                print('cleaccn',cleaned_data)
                data={
                    'ms_id':MSID,
                    'ms_payload':cleaned_data
                } 
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                print('response',response)
                if response['status_code'] ==  0:                  
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('user_list')
                else:
                    messages.info(request, "Oops..! Application Failed to Submitted..")
        else:
            print('form-error')
            form = UserRegistrationForm(initial=record)

        context = {
            'form': form, 'user_edit': 'active', 'user_edit_show': 'show','userprofile':user_profile,'record':record
        }
        return render(request, 'UserManagement/user_edit.html', context)
    except Exception as error:
        return render(request, "error.html", {"error": error})   

def user_view(request,pk):
    try:
        token = request.session['user_token']

        MSID= get_service_plan('userprofile list')
        if MSID is None:
            print('MISID not found') 
        payload_form={

        }     
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        } 
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
    
        userprofile=response['data']

        print('data is comming',pk)
        MSID= get_service_plan('get user')
        if MSID is None:
            print('MISID not found') 
        payload_form={
            'id':pk
        }     
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        } 
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        print('response',response['data'])
        if response['status_code'] ==  0:                  
            messages.info(request, "Well Done..! Application Submitted..")
            records=response['data'][0]
            form = UserRegistrationForm(initial=records)
            
        #records = User.objects.all()
            context = {
                'user_list': 'active', 'user_list_show': 'show', 'form': form,'screen_name':'User','userprofile':userprofile,'records':records
            }
            return render(request, 'UserManagement/user_view.html', context)
    except Exception as error:
        return render(request, "error.html", {"error": error})   
    
def user_delete(request,pk):
    try:
        token = request.session['user_token']

        MSID= get_service_plan('user delete')
        if MSID is None:
            print('MISID not found') 
        payload_form={
            'id':pk
        }     
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        } 
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
    
        if response['status_code'] ==  0:                  
            messages.info(request, "Well Done..! Application Submitted..")
            return redirect('user_list')          
        #records = User.objects.all()
    except Exception as error:
        return render(request, "error.html", {"error": error})   




def roles(request):
    try:
        token = request.session['user_token']
        MSID= get_service_plan('role list')
        if MSID is None:
            print('MISID not found') 
        payload_form={

        }     
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        } 
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        print('response',response)
        print('response',response['data'])
        if response['status_code'] ==  1:                  
            messages.info(request, "Well Done..! Application Submitted..")
            print('error',response['data'])
        records=response['data']
        #records=Role.objects.all()
        context={
            'records':records,'roles': 'active', 'roles_show': 'show'
        }
        return render(request,'UserManagement/roles.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})   

def roles_create(request):
    try:
        token = request.session['user_token']

        form = RoleForm()
        if request.method=='POST':
            form = RoleForm(request.POST)
            if form.is_valid():
                MSID= get_service_plan('role create')
                if MSID is None:
                    print('MISID not found') 
                cleaned_data=form.cleaned_data
                    
                data={
                    'ms_id':MSID,
                    'ms_payload':cleaned_data
                } 
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
            
                if response['status_code'] ==  0:                  
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('roles')
                else:
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 
        
        context={
            'roles': 'active', 'roles_show': 'show','form':form,'screen_name':"Roles"
        }
        return render(request,'create.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})   

def roles_edit(request,pk):
    try:
        token = request.session['user_token']

        MSID= get_service_plan('role list')
        if MSID is None:
            print('MISID not found') 
        payload_form={
            'id':pk
        }     
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        } 
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
    
        if response['status_code'] ==  0:                  
            messages.info(request, "Well Done..! Application Submitted..")
            print('error',response['data'])
        record=response['data'][0]
        
        #record = Role.objects.get(pk=pk)
        form = RoleForm(initial=record)
        if request.method=='POST':
            form = RoleForm(request.POST,initial=record)
            if form.is_valid():
                MSID= get_service_plan('role edit')
                if MSID is None:
                    print('MISID not found') 
                cleaned_data=form.cleaned_data
                cleaned_data['id']=pk  
                data={
                    'ms_id':MSID,
                    'ms_payload':cleaned_data
                } 
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
            
                if response['status_code'] ==  0:                  
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('roles')
                else:
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 
                
        context={
            'roles': 'active', 'roles_show': 'show','form':form,'screen_name':"Roles"
        }
        return render(request,'create.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})   

def roles_delete(request,pk):
    try:
        token = request.session['user_token']

        MSID= get_service_plan('role delete')
        if MSID is None:
            print('MISID not found') 
        payload_form={
            'id':pk
        }     
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        } 
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        print('response',response)
        if response['status_code'] ==  0:                  
            messages.info(request, "Well Done..! Application Submitted..")
            return redirect('roles')
        else:
            messages.info(request, "Oops..! Application Failed to Submitted..")

        #Role.objects.get(pk=pk).delete()
    except Exception as error:
        return render(request, "error.html", {"error": error})   
    

def permission(request, pk):
    try:
        # Fetch all Function objects
        token = request.session['user_token']
        MSID= get_service_plan('function all')
        if MSID is None:
            print('MISID not found') 
        payload_form={

        }     
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        } 
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
    
        if response['status_code'] ==  1:                  
            messages.info(request, "Well Done..! Application Submitted..")
            records=[]
        records=response['data']
        print('recordsa',records)
        MSID= get_service_plan('get user permission')
        if MSID is None:
            print('MISID not found') 
        payload_form={
            'id':pk
        }     
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        } 
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
    
        if response['status_code'] ==  1:                  
            messages.info(request, "Well Done..! Application Submitted..")
            permission_records=[]
        permission_records=response['data']
        
        permission_id_list = [data['id'] for data in permission_records]
    
        if request.method == 'POST':
            # Fetch permissions from POST data
            permission_ids = request.POST.getlist('permission')
            print('permission id',permission_ids)
            if permission_ids:
                MSID= get_service_plan('update user permission')
                if MSID is None:
                    print('MISID not found') 
                payload_form={
                    'id':pk,
                    'permission':permission_ids
                }     
                data={
                    'ms_id':MSID,
                    'ms_payload':payload_form
                } 
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
            
                if response['status_code'] ==  0:                  
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('roles')

                else:
                    messages.info(request, "Oops..! Application Failed to Submitted..")

            return redirect('roles')

        # Prepare the context for rendering
        context = {
            'roles': 'active', 
            'roles_show': 'show', 
            'screen_name': "Permission",
            'records': records,'permission_id_list':permission_id_list
        }
        return render(request, 'UserManagement/permission.html', context)
    
    except Exception as error:
        return render(request, "error.html", {"error": error})   



# Example usage in a view:
def function_setup(request):
    try:
        token = request.session['user_token']

        MSID= get_service_plan('function setup')
        if MSID is None:
            print('MISID not found') 
        payload_form={
          
        }     
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        } 
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
    
        if response['status_code'] ==  1:                  
            messages.info(request, "Well Done..! Application Submitted..")
        
        return redirect(request.META.get('HTTP_REFERER', '/'))
    
    except Exception as error:
        return render(request, "error.html", {"error": error})   
    
def multi_factor_authentication(request):
    try:
        token = request.session['user_token']

        otp = request.POST.get('otp')
        if request.method == "POST":
            MSID= get_service_plan('multi factor authentication')
            if MSID is None:
                print('MISID not found') 
            payload_form={
                'otp':otp
            }     
            data={
                'ms_id':MSID,
                'ms_payload':payload_form
            } 
            json_data = json.dumps(data)
            response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
            if response['status_code'] ==  1:    
                otp_error = 'Invailed OTP'              
                return render(request, 'UserManagement/otp_verification.html',{'otp_error':otp_error})
        
            return redirect('dashboard')
        else:
            MSID= get_service_plan('generate and send otp')
            if MSID is None:
                print('MISID not found') 
            payload_form={
                
            }     
            data={
                'ms_id':MSID,
                'ms_payload':payload_form
            } 
            json_data = json.dumps(data)
            response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        
            return render(request, 'UserManagement/otp_verification.html')
    except Exception as error:
        return render(request, "error.html", {"error": error})  


def login(request):
    try:
        # Check if the request method is POST
        
        if request.method == "POST":
            email = request.POST.get('email')
            password = request.POST.get('password')
            payload = {        
                "email" : email,
                "password" : password
            }
            # Convert payload to JSON format
            json_payload = json.dumps(payload)
            print('json_payload',json_payload)
            ENDPOINT = 'api/token/'
            login_response = call_post_method_without_token(BASEURL+ENDPOINT,json_payload)
            print('login_response',login_response)
            
            if login_response.status_code == 200:
                login_tokes = login_response.json()
                request.session['user_token']=login_tokes['access_token']
                request.session['user_data']=login_tokes['user_data']


                request.session['user_permissions'] = login_tokes['user_permission']['permission']
                user_data=login_tokes['user_data']
                print('user_data',request.session['user_permissions'])
                #===============getting User Permission==============
                
                # MSID= get_service_plan('get permissions for session')
                # if MSID is None:
                #     print('MISID not found') 
                # payload_form={
                #     # 'user_profile_id':user_data['user_profile']
                # }     
                # data={
                #     'ms_id':MSID,
                #     'ms_payload':payload_form
                # } 
                # json_data = json.dumps(data)
                # response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                # print('response_permission',response)
                # request.session['permission'] = response['data_list']
                
                if user_data['multi_factor_auth'] or user_data['is_superuser']:
                    if user_data['is_superuser']:
                        return redirect('company_selecting')
                    else:
                        return redirect('dashboard')
                elif not user_data['multi_factor_auth']:
                    return redirect('multi_factor_authentication')

            else:
                login_error='Invalid Username or Password'
                context={"login_error":login_error}
                return render(request, 'Auth/login.html',context)
          
        return render(request, 'Auth/login.html')
    except Exception as error:
        return HttpResponse(f'<h1>{error}</h1>')
    
  

def dashboard(request):
    return render(request, 'dashboard.html',{'dashboard':'active'})


def logout(request):
    try:
        token = request.session['user_token']
        MSID= get_service_plan('logout')
        if MSID is None:
            print('MISID not found') 
        payload_form={

        }     
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        } 
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        print('response',response)
        print('response',response['data'])
        if response['status_code'] ==  0:   
            request.session.delete()

            return redirect('login')
        else:
            return redirect('dashboard')
    except Exception as error:
        return render(request, "error.html", {"error": error})   

def change_password(request):
    try:
        token = request.session['user_token']
        MSID = get_service_plan('change password')
        if MSID is None:
            print('MSID not found') 
        user_data = request.session["user_data"]
        if request.method == 'POST':
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            if new_password != confirm_password:
                return render(request, "UserManagement/password_change_form.html", {"error": "New passwords do not match."})
            payload_form = {
                'user_id':user_data['id'],
                'old_password': old_password,
                'new_password': new_password,
                'confirm_password':confirm_password,
            }
            data = {
                'ms_id': MSID,
                'ms_payload': payload_form
            }
            json_data = json.dumps(data)
            response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
            print('response', response)
            if response['status_code'] == 0:
                return redirect('logout')
            else:
                return render(request, "UserManagement/password_change_form.html", {"error": response['data']})
        else:
            return render(request, "UserManagement/password_change_form.html")
    except Exception as error:
        return render(request, "error.html", {"error": error})

def forgot_password(request):
    try:
        if request.method == 'POST':
            email = request.POST.get('email')
            otp = request.POST.get('otp')
            if not otp:
                MSID = get_service_plan('forgot password')
                print('MSID',MSID)
                if MSID is None:
                    print('MSID not found') 
                payload_form = {
                    'email':email
                }
                data = {
                    'ms_id': MSID,
                    'ms_payload': payload_form
                }
                json_data = json.dumps(data)
                url = BASEURL + 'micro-service-forgot/'
                print('url',url)
                response = call_post_method_without_token(url, json_data)
                print('response2', response)
                if response.status_code == 200:
                    return render(request, "UserManagement/otp_verification.html",{'email':email})
                else:
                    return render(request, "Auth/forget_password_form.html", {"error": 'Invalid email ID'})
            else:
                        
                MSID = get_service_plan('verify forgot password')
                if MSID is None:
                    print('MSID not found') 
                payload_form = {
                    'email':email,
                    'otp':otp
                }
                data = {
                    'ms_id': MSID,
                    'ms_payload': payload_form
                }
                json_data = json.dumps(data)
                url = BASEURL + 'micro-service-forgot/'
                print('url',url)
                response = call_post_method_without_token(url, json_data)
                print('response1', response)
                if response.status_code == 200:
                    return redirect('set_password',email=email)
                else:
                    return render(request, "UserManagement/otp_verification.html",{'email':email,'otp_error':response['data']})
        else:
            return render(request, "Auth/forget_password_form.html")
    except Exception as error:
        return render(request, "error.html", {"error": error})

def set_password(request,email):
    token = request.session['user_token']
    user_data = request.session['user_data']
    print('token--',token)
    print('user_data--',user_data)
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        MSID = get_service_plan('set password')
        if MSID is None:
            print('MSID not found') 
        payload_form = {
            'email':email,
            'new_password':new_password,
            'confirm_password':confirm_password
        }
        data = {
            'ms_id': MSID,
            'ms_payload': payload_form
        }
        json_data = json.dumps(data)
        url = BASEURL + 'micro-service-forgot/'
        response = call_post_method_without_token(url, json_data)
        print('response', response)
        if response.status_code == 200:
            return redirect('login')
        else:
            return render(request, "Auth/set_password.html",{'email':email,'set_password_error':response['data']})
    else:
        return render(request, "Auth/set_password.html",{'email':email})
def userprofile_list(request):
    try:
        token = request.session['user_token']
        MSID= get_service_plan('userprofile list')
        if MSID is None:
            print('MISID not found') 
        payload_form={

        }     
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        } 
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        print('response',response)
        print('response',response['data'])
        if response['status_code'] == 201:                
            messages.info(request, "Well Done..! Application Submitted..")
            print('error',response['data'])
        records=response['data']
        print('records',records)
        context={
            'records':records,'userprofile': 'active', 'userprofile_show': 'show'
        }
        return render(request,'UserManagement/user_profile_list.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})   

def userprofile_create(request):
    try:
        token = request.session['user_token']

        MSID= get_service_plan('role list')
        if MSID is None:
            print('MISID not found') 
        payload_form={

        }     
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        } 
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        roles_records = response['data']
        
        form = UserProfileForm(role=roles_records)
        if request.method=='POST':
            form = UserProfileForm(request.POST,role=roles_records)
            if form.is_valid():
                                
                MSID= get_service_plan('userprofile create')
                if MSID is None:
                    print('MISID not found') 
                cleaned_data=form.cleaned_data
                    
                data={
                    'ms_id':MSID,
                    'ms_payload':cleaned_data
                } 
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
            
                if response['status_code'] ==  0:                  
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('userprofile_list')
                else:
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 
        
        context={
            'roles': 'active', 'roles_show': 'show','form':form,'screen_name':"User Profile Creation"
        }
        return render(request,'UserManagement/UserProfile.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})  

def userprofile_edit(request,id):
    try:
        token = request.session['user_token']

        MSID= get_service_plan('role list')
        if MSID is None:
            print('MISID not found') 
        payload_form={

        }     
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        } 
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        roles_records = response['data']


        MSID= get_service_plan('userprofile list')
        if MSID is None:
            print('MISID not found') 
        payload_form={
            'id':id
        }     
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        } 
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
    
        if response['status_code'] ==  0:                  
            messages.info(request, "Well Done..! Application Submitted..")
            print('error',response['data'])
        record=response['data'][0]
        
        #record = Role.objects.get(pk=pk)
        form = UserProfileForm(initial=record,role=roles_records)
        if request.method=='POST':
            form = UserProfileForm(request.POST,initial=record,role=roles_records)
            if form.is_valid():
                MSID= get_service_plan('userprofile edit')
                if MSID is None:
                    print('MISID not found') 
                cleaned_data=form.cleaned_data
                print('cleaned_data',cleaned_data)
                cleaned_data['id']=id  
                data={
                    'ms_id':MSID,
                    'ms_payload':cleaned_data
                } 
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
            
                if response['status_code'] ==  0:                  
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('userprofile_list')
                else:
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 
                
        context={
            'roles': 'active', 'roles_show': 'show','form':form,'screen_name':"Roles"
        }
        return render(request,'UserManagement/UserProfile.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})   
def userprofile_delete(request,id):
    try:
        token = request.session['user_token']

        MSID= get_service_plan('userprofile delete')
        if MSID is None:
            print('MISID not found') 
        payload_form={
            'id':id
        }     
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        } 
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        print('response',response)
        if response['status_code'] ==  0:                  
            messages.info(request, "Well Done..! Application Submitted..")
            return redirect('userprofile_list')
        else:
            messages.info(request, "Oops..! Application Failed to Submitted..")

        #Role.objects.get(pk=pk).delete()
    except Exception as error:
        return render(request, "error.html", {"error": error})   