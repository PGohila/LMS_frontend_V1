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
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('user_list')
                else:
                    messages.info(request, "Oops..! Application Failed to Submitted..")
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
    
        if response['status_code'] ==  0:                  
            messages.info(request, "Well Done..! Application Submitted..")
            print('error',response['data'])
        role=response['data']

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
    
        if response['status_code'] ==  0:                  
            messages.info(request, "Well Done..! Application Submitted..")
            print('error',response['data'])
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
            form = UserRegistrationForm(initial=record)

        context = {
            'form': form, 'user_edit': 'active', 'user_edit_show': 'show','role':role,'record':record
        }
        return render(request, 'UserManagement/user_edit.html', context)
    except Exception as error:
        return render(request, "error.html", {"error": error})   

def user_view(request,pk):
    try:
        token = request.session['user_token']
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
                'user_list': 'active', 'user_list_show': 'show', 'form': form,'screen_name':'User'
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
                user_data=login_tokes['user_data']
                print('user_data',user_data)
                request.session['user_data']=login_tokes['user_data']
                return redirect('dashboard')
            else:
                login_tokes = login_response.json()
                login_error='Invalid Username and Password'
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
            return redirect('login')
        else:
            return redirect('dashboard')
    except Exception as error:
        return render(request, "error.html", {"error": error})   


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
        if response['status_code'] ==  1:                  
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
        return render(request,'create.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})  

def userprofile_edit(request,pk):
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
        form = UserProfileForm(initial=record,role=roles_records)
        if request.method=='POST':
            form = UserProfileForm(request.POST,initial=record,role=roles_records)
            if form.is_valid():
                MSID= get_service_plan('userprofile edit')
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
def userprofile_delete(request,pk):
    try:
        token = request.session['user_token']

        MSID= get_service_plan('userprofile delete')
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