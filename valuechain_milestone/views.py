from django.shortcuts import render,redirect
import json
from mainapp.views import get_service_plan,call_post_method_with_token_v2
# Create your views here.
from django.conf import settings
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
        print("================",loantype_records)
        context = {'loantype': milestone_loantypes}
        return render(request,'valuechain/setup_valuechain.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})  