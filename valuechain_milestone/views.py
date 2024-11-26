from django.shortcuts import render,redirect
import json
from mainapp.views import get_service_plan,call_post_method_with_token_v2
# Create your views here.
from django.conf import settings
from django.http import JsonResponse
import json
from valuechain_milestone.forms import *
from django.contrib import messages
BASEURL = settings.BASEURL
ENDPOINT = 'micro-service/'


def valuechain_setups(request):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')

        # getting disbursement beneficiary is milestone in loan type
        MSID = get_service_plan('view loantype') # view_loantype
        if MSID is None:
            print('MSID not found')
        data = {'ms_id': MSID,'ms_payload': {'company_id':company_id}}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        
        loantype_records = response['data']
        milestone_loantypes = [data for data in loantype_records if data['disbursement_beneficiary'] == 'pay_milestone']
        
        if request.method == "POST":
            print("pJDNSN")
            active = request.POST.getlist('is_active')
            valuechain_name = request.POST.getlist('ValueChain')
            max_amt = request.POST.getlist('MaxAmount')
            min_amt = request.POST.getlist('MinAmount')
            description = request.POST.getlist('description')
            loantype = request.POST.get('LoanType2')
  
            for index,data in enumerate(valuechain_name):
                # saving valuechain setups
                MSID = get_service_plan('create valuechainsetup') # create_valuechainsetup
                if MSID is None:
                    print('MSID not found')
                payloads = {'company_id':company_id,'loan_type_id':loantype,'valuechain_name':valuechain_name[index],'max_amount':max_amt[index],'min_amount':min_amt[index],'status':True,'description':description[index]}
                data = {'ms_id': MSID,'ms_payload': payloads}
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
                if response['status_code'] == 1:
                    return render(request,'error.html',{'error':str(response['data'])})
            return redirect('valuechain_setups')
        context = {'loantype': milestone_loantypes}
        return render(request,'valuechain/setup_valuechain.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})  
    
def get_valuechain_data(request):
    token = request.session['user_token']
    company_id = request.session.get('company_id')

    if request.method == 'POST':
        
        data = json.loads(request.body)
        loan_type_id = data.get('loan_type_id')

        if loan_type_id:
            MSID = get_service_plan('getting valuechainsetups') # getting_valuechainsetups
            if MSID is None:
                print('MSID not found')
            payloads = {'company_id':company_id,'loantype_id':loan_type_id}
            data = {'ms_id': MSID,'ms_payload': payloads}
            json_data = json.dumps(data)
            response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
         
            if response['status_code'] == 1:
                return render(request,'error.html',{'error':str(response['data'])})
            value_chain_data = response['data']
            
            return JsonResponse({"success": True, "value_chain_data": value_chain_data})
        else:
            return JsonResponse({"success": False, "message": "No data found."})
    return JsonResponse({"success": False, "message": "Invalid request method."})

#============ function for valuechainsetup Edit ===================

def valuechainsetup_edit(request,pk):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        
        MSID = get_service_plan('getting valuechainsetups') # getting_valuechainsetups
        if MSID is None:
            print('MSID not found')
        payloads = {'valuechain_id':pk}
        data = {'ms_id': MSID,'ms_payload': payloads}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
            # return redirect('valuechain_setups')
        form = ValueChainSetupForm(initial=response['data'][0])
        if request.method == 'POST':
            
            MSID = get_service_plan('valuechain setup edit')
            if MSID is None:
                print('MISID not found')
            form = ValueChainSetupForm(request.POST)
            if form.is_valid():
                cleaned_data = form.cleaned_data          
                cleaned_data['valuechain_id'] = pk    
                data = {'ms_id':MSID,'ms_payload':cleaned_data }
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                print("dswdghiwe",response)
                if response['status_code'] == 0:
                    messages.info(request, "Well Done..! Application Submitted..")
            return redirect('valuechain_setups')

        context = {'form':form}
        return render(request,'valuechain/edit_valuechainsetup.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})  

def valuechainsetup_delete(request,pk):
    try:
        token = request.session['user_token']
        MSID = get_service_plan('valuechain setup delete') # valuechain_setup_delete
        if MSID is None:
            print('MSID not found')
        payloads = {'valuechain_id':pk}
        data = {'ms_id': MSID,'ms_payload': payloads}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        return redirect('valuechain_setups')
    except Exception as error:
        return render(request, "error.html", {"error": error})  

#================== Set milestones ===============

def disply_valuechain(request):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')

        # getting disbursement beneficiary is milestone in loan type
        MSID = get_service_plan('view loantype') # view_loantype
        if MSID is None:
            print('MSID not found')
        data = {'ms_id': MSID,'ms_payload': {'company_id':company_id}}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        
        loantype_records = response['data']
        milestone_loantypes = [data for data in loantype_records if data['disbursement_beneficiary'] == 'pay_milestone']
        context = {'loantype': milestone_loantypes}
        return render(request,'valuechain/disply_valuechain.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})

def create_milestone(request,pk): # pk = is value chjain id
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
  
        # getting disbursement beneficiary is milestone in loan type
        MSID = get_service_plan('getting valuechainsetups') # getting_valuechainsetups
        if MSID is None:
            print('MSID not found')
        data = {'ms_id': MSID,'ms_payload': {'valuechain_id':pk}}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        valuechain_details = response['data'][0]

        #=========== getting all milestones ================
     
        MSID = get_service_plan('getting milestonesetup') # getting_milestonesetup
        if MSID is None:
            print('MSID not found')
        data = {'ms_id': MSID,'ms_payload': {'company_id':company_id,'valuechain_id':pk}}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        milestone_details = response['data']

        #================== saveing ==================
        if request.method == "POST":
            
            MSID = get_service_plan('create milestonesetup') # create_milestonesetup
            if MSID is None:
                print('MSID not found')
            loantype_id = valuechain_details['loan_type']['id']
            payloads = {'company_id':company_id,'loan_type':loantype_id,'valuechain_id':pk,'milestone_name':request.POST.get('milestone_name'),'max_amount':request.POST.get('MaxAmount'),'min_amount':request.POST.get('MinAmount'),'description':request.POST.get('description')}
            data = {'ms_id': MSID,'ms_payload': payloads}
            json_data = json.dumps(data)
            response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
            if response['status_code'] == 1:
                return render(request,'error.html',{'error':str(response['data'])})
            
            return redirect(f'/create_milestone/{pk}')
        context = {'valuechain_details':valuechain_details,'milestone_details':milestone_details}
        return render(request,'valuechain/create_milestones.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})
    
#================ Edit Milestone Details ================
def milestonesetup_edit(request,pk):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        
        MSID = get_service_plan('getting milestonesetup') # getting_milestonesetup
        if MSID is None:
            print('MSID not found')
        payloads = {'miletone_id':pk,'company_id':company_id}
        data = {'ms_id': MSID,'ms_payload': payloads}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
            # return redirect('valuechain_setups')
        milestones_detail = response['data'][0]
        form = mileStoneSetupForm(initial=milestones_detail)

        if request.method == 'POST':
            
            MSID = get_service_plan('milestone setup edit') # milestone_setup_edit
            if MSID is None:
                print('MISID not found')
            form = mileStoneSetupForm(request.POST)
            if form.is_valid():
                cleaned_data = form.cleaned_data          
                cleaned_data['milestone_id'] = pk    
                data = {'ms_id':MSID,'ms_payload':cleaned_data }
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                print("dswdghiwe",response)
                if response['status_code'] == 0:
                    messages.info(request, "Well Done..! Application Submitted..")
            return redirect(f"/create_milestone/{milestones_detail['valuechain_id']['id']}")

        context = {'form':form}
        return render(request,'valuechain/edit_milestonesetup.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})  

def milestonesetup_delete(request,pk):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')

        MSID = get_service_plan('getting milestonesetup') # getting_milestonesetup
        if MSID is None:
            print('MSID not found')
        payloads = {'miletone_id':pk,'company_id':company_id}
        data = {'ms_id': MSID,'ms_payload': payloads}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
            # return redirect('valuechain_setups')
        milestones_detail = response['data'][0]

        MSID = get_service_plan('milestone setup delete') # milestone_setup_delete
        if MSID is None:
            print('MSID not found')
        payloads = {'milestone_id':pk}
        data = {'ms_id': MSID,'ms_payload': payloads}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        return redirect(f"/create_milestone/{milestones_detail['valuechain_id']['id']}")
    except Exception as error:
        return render(request, "error.html", {"error": error})

# ================ create milestone Stages ========================
def add_milestonestages(request,pk): # pk = is a milestone id
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')

        # getting milestone Details
        MSID = get_service_plan('getting milestonesetup') # getting_milestonesetup
        if MSID is None:
            print('MSID not found')
        payloads = {'miletone_id':pk,'company_id':company_id}
        data = {'ms_id': MSID,'ms_payload': payloads}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
            # return redirect('valuechain_setups')
        milestones_detail = response['data'][0]
        

        #========== getting all activities =============
        MSID = get_service_plan('getting milestonestagessetup') # getting_milestonestagessetup
        if MSID is None:
            print('MSID not found')
        payloads = {'miletone_id':pk,'company_id':company_id}
        data = {'ms_id': MSID,'ms_payload': payloads}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
            # return redirect('valuechain_setups')
        activities_detail = response['data']

        if request.method == "POST":
            MSID = get_service_plan('create stagesetup') # create_stagesetup
            if MSID is None:
                print('MSID not found')
            payloads = {'company_id':company_id,'milestone_id':pk,'stage_name':request.POST.get('stage_name'),'min_amount':request.POST.get('MaxAmount'),'max_amount':request.POST.get('MinAmount'),'sequence':request.POST.get('sequence'),'description' : request.POST.get('description')}
            data = {'ms_id': MSID,'ms_payload': payloads}
            json_data = json.dumps(data)
            response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
            if response['status_code'] == 1:
                return render(request,'error.html',{'error':str(response['data'])})
            print("============",response)
            return redirect(f"/add_milestonestages/{pk}")

  
        context = {'milestones_detail':milestones_detail,'activities_detail':activities_detail}
        return render(request,"valuechain/add_milestonestage.html",context)
    except Exception as error:
        return render(request, "error.html", {"error": error})
    
#================ Edit activities Details ================
def activities_edit(request,pk):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        
        MSID = get_service_plan('getting milestonestagessetup') # getting_milestonestagessetup
        if MSID is None:
            print('MSID not found')
        payloads = {'stages_id':pk,'company_id':company_id}
        data = {'ms_id': MSID,'ms_payload': payloads}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
            # return redirect('valuechain_setups')
        activities_detail = response['data'][0]
        form = MilestoneStageForm(initial=activities_detail)

        if request.method == 'POST':
            
            MSID = get_service_plan('stages setup edit') # stages_setup_edit
            if MSID is None:
                print('MISID not found')
            form = MilestoneStageForm(request.POST)
            if form.is_valid():
                cleaned_data = form.cleaned_data          
                cleaned_data['stages_id'] = pk    
                data = {'ms_id':MSID,'ms_payload':cleaned_data }
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                print("========",response)
                if response['status_code'] == 0:
                    messages.info(request, "Well Done..! Application Submitted..")
                return redirect(f"/add_milestonestages/{activities_detail['milestone_id']['id']}")

        context = {'form':form}
        return render(request,'valuechain/edit_activitiessetup.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})  

def activities_delete(request,pk):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')


        MSID = get_service_plan('getting milestonestagessetup') # getting_milestonestagessetup
        if MSID is None:
            print('MSID not found')
        payloads = {'stages_id':pk,'company_id':company_id}
        data = {'ms_id': MSID,'ms_payload': payloads}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        milestones_detail = response['data'][0]

        MSID = get_service_plan('stages setup delete') # stages_setup_delete
        if MSID is None:
            print('MSID not found')
        payloads = {'stages_id':pk}
        data = {'ms_id': MSID,'ms_payload': payloads}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
   
        return redirect(f"/create_milestone/{milestones_detail['milestone_id']['valuechain_id']['id']}")
    except Exception as error:
        return render(request, "error.html", {"error": error})


def show_trenches(request,pk): # pk = is the loan id
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')

        #============ getting Loan id ===============
        MSID = get_service_plan('view loan') # view_loan
        if MSID is None:
            print('MSID not found')
        payloads = {'loan_id':pk}
        data = {'ms_id': MSID,'ms_payload': payloads}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})

        loan_data = response['data'][0]

        #=============== getting valuechainsetup for loantype ==================
        MSID = get_service_plan('getting valuechainsetups') # getting_valuechainsetups
        if MSID is None:
            print('MSID not found')
        payloads = {'company_id':company_id,'loantype_id':loan_data['loanapp_id']['loantype']['id']}
        data = {'ms_id': MSID,'ms_payload': payloads}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        
        valuechain_data = response['data']

        #===================== getting milestones ======================
        MSID = get_service_plan('getting milestonesetup') # getting_milestonesetup
        if MSID is None:
            print('MSID not found')
        payloads = {'company_id':company_id}
        data = {'ms_id': MSID,'ms_payload': payloads}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        
        MSID = get_service_plan('getting loan tranches') # getting_loan_tranches
        if MSID is None:
            print('MSID not found')
        payloads = {'company_id':company_id}
        data = {'ms_id': MSID,'ms_payload': payloads}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})

        context = {'loan_data':loan_data,'valuechain_data':valuechain_data}
        return render(request,'valuechain/show_trenches.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})
