from django.urls import path
from .views import *
from .EDMS_views import *

urlpatterns = [
    
    path("company_selecting/",company_selecting, name="company_selecting"),
    path("dashboard/",dashboard, name="dashboard"),

    path('company/', company_create, name='company'),
    path('company-view/', company_view, name='company_view'),
    path('company-edit/<pk>/', company_edit, name='company_edit'),
    path('company-delete/<pk>/', company_delete, name='company_delete'),
    path('company-list/', customer_list, name='customer_list'),
  
    path('customer/', customer_create, name='customer'),
    path('customer-view', customer_view, name='customer_view'),
    path('customer-edit/<pk>/', customer_edit, name='customer_edit'),
    path('customer-delete/<pk>/', customer_delete, name='customer_delete'),

    path('customer_list/', customer_list, name='customerlist'),
    path('uploadmultidocument_customer/<pk>/', uploadmultidocument_customer, name='uploadmultidocumentcustomer'),

    # path('customerdocuments/', customerdocuments_create, name='customerdocuments'),
    path('customer_view_fordoc/', customer_view_fordoc, name='customer_view_fordoc'),

    path('loanapplication/', loanapplication_create, name='loanapplication'),
    path('loanapplication-view/', loanapplication_view, name='loanapplication_view'),
    path('loanapplication_summary/<pk>/', loanapplication_summary, name='loanapplication_summary'),
    path('loanapplication-edit/<pk>/', loanapplication_edit, name='loanapplication_edit'),
    path('loanapplication-delete/<pk>/', loanapplication_delete, name='loanapplication_delete'),
    path('view_loan_applications/', view_loan_applications, name='view_loanapplications'),
    path('application_status_tracking/<pk>/', application_status_tracking, name='applicationstatus_tracking'),

    path('document_varification/', document_varification, name='document_varification'),
    path('verify_documents/<pk>/', verify_documents, name='verify_documents'),

    path('show_active_applications/', show_active_applications, name='show_active_applications'),
    path('eligibility_status/<pk>/', eligibility_status, name='eligibility_status'),

    path('loan_risk_assessment/', loan_risk_assessment_list, name='assessmentlist'),
    path('loan_risk_assessment/<pk>/', loan_risk_assessment_detail, name='loan_risk_assessment_detail'),

    path('loan_approval_view/', loan_approval_view, name='loanapprovalview'),
    path('loan_approval/<pk>/', loan_approval, name='loanapproval'),

    path('list_approved_applications/', list_approved_applications, name='listapprovedapplications'),
    path('create_agreement/<pk>/', create_agreement, name='createagreement'),
    path('agreement_review/<loanapp_id>/<template_id>/', agreement_review, name='agreement_review'),
    path('list_agreement/', list_agreement, name='list_agreement'),
    path('agreement_confirmation/<pk>', agreement_confirmation, name='agreementconfirmation'),
    path('edit_agreement/<pk>', edit_agreement, name='editagreement'),

    path('disbursement_request/', disbursement_request, name='disbursementrequest'),
    path('disply_agreed_agreement/<pk>', disply_agreed_agreement, name='displyagreedagreement'),
    path('disply_loans/', disply_loans, name='disply_loans'),
    path('disbursement/<loanid>/', disbursement_create, name='disbursement'),
    path('disbursement_details/', disbursement_details, name='disbursement_details'),
    path('show_disbursement_details/<pk>/', show_disbursement_details, name='show_disbursement_details'),

    path('show_loandetails/',show_loandetails,name='show_loandetails'),
    path('create_collateral/<pk>/', create_collateral, name='create_collateral'),
    # path('collaterals/', collaterals_create, name='collaterals'),
    path('collaterals-view/', collaterals_view, name='collaterals_view'),
    path('collateral_details/<pk>/', collateral_details, name='collateral_details'),
    path('collaterals-edit/<pk>/', collaterals_edit, name='collaterals_edit'),
    path('collaterals-delete/<pk>/', collaterals_delete, name='collaterals_delete'),
    
    path('disbursed_loans/', disbursed_loans, name='disbursed_loans'),
    path('repayment_schedule/<pk>/', repayment_schedule, name='repayment_schedule'),
    path('disbursedloans_foroverview/', disbursedloans_foroverview, name='disbursedloans_foroverview'),
    path('schedule_overview/<pk>/', schedule_overview, name='schedule_overview'),
    path('loancalculators/', loancalculators_create, name='loancalculators'),

    path('loan_list/', loan_list, name='loan_list'),
    path('account_list/<id>', account_list, name='account_list'),
    
#--------------- repayment 2 ----------------------
    path('disbursed_loans1/', disbursed_loans1, name='disbursed_loans1'),
    path('repayment_schedule1/<pk>/', repayment_schedule1, name='repayment_schedule1'),
    path('disbursedloans_foroverview1/', disbursedloans_foroverview1, name='disbursedloans_foroverview1'),
    path('schedule_overview1/<pk>/', schedule_overview1, name='schedule_overview1'),
    path('payment_process/<schedule_id>/', payment_process, name='payment_process'),

    #=============== Penalties =====================
    path('disply_penaltyloans/', disply_penaltyloans, name='disply_penaltyloans'),

    #================== Setting urls ================
    path('identificationtype/', identificationtype_create, name='identificationtype'),
    path('identificationtype-view/', identificationtype_view, name='identificationtype_view'),
    path('identificationtype-edit/<pk>/', identificationtype_edit, name='identificationtype_edit'),
    path('identificationtype-delete/<pk>/', identificationtype_delete, name='identificationtype_delete'),

    path('bankaccount/', bankaccount_create, name='bankaccount'),
    path('bankaccount-view/', bankaccount_view, name='bankaccount_view'),
    path('bankaccount-edit/<pk>/', bankaccount_edit, name='bankaccount_edit'),
    path('bankaccount-delete/<pk>/', bankaccount_delete, name='bankaccount_delete'),

    path('currency/', currency_create, name='currency'),
    path('currency-view/', currency_view, name='currency_view'),
    path('currency-edit/<pk>/', currency_edit, name='currency_edit'),
    path('currency-delete/<pk>/', currency_delete, name='currency_delete'),

    path('paymentmethod/', paymentmethod_create, name='paymentmethod'),
    path('paymentmethod-view/', paymentmethod_view, name='paymentmethod_view'),
    path('paymentmethod-edit/<pk>/', paymentmethod_edit, name='paymentmethod_edit'),
    path('paymentmethod-delete/<pk>/', paymentmethod_delete, name='paymentmethod_delete'),

    path('collateraltype/', collateraltype_create, name='collateraltype'),
    path('collateraltype-view/', collateraltype_view, name='collateraltype_view'),
    path('collateraltype-edit/<pk>/', collateraltype_edit, name='collateraltype_edit'),
    path('collateraltype-delete/<pk>/', collateraltype_delete, name='collateraltype_delete'),

    path('loantype/', loantype_create, name='loantype'),
    path('loantype-view/', loantype_view, name='loantype_view'),
    path('loantype-edit/<pk>/', loantype_edit, name='loantype_edit'),
    path('loantype-delete/<pk>/', loantype_delete, name='loantype_delete'),


    #==================DMS=====================
    path('matter_workspace/', customer_workspace,name='matter_workspace'),
    path('document_storage/<entity_id>/', document_storage, name='document_storage'),
    path('folder/<entity_id>/<folder_id>/', folder, name='folder'),
    path('client_folder_delete/<entity_id>/<folder_id>/',client_folder_delete,name="client_folder_delete"),

    path('create_folder/<entity_id>/', create_folder,name='create_folder'),
    path('create_sub_folder/<entity_id>/<folder_id>/', create_sub_folder,name='create_sub_folder'),

    path('upload_document/<entity_id>/<folder_id>/', upload_document,name='upload_document'),
    path('document_category/', document_category,name='document_category'),
    path('department/', department,name='department'),
    path('document_type/', document_type,name='document_type'),
    path('document_entity/', document_entity,name='document_entity'),

    path('document_view/<entity_id>/<folder_id>/<document_id>/', document_view,name='document_view'),
    path('document_version/<document_id>/', document_version,name='document_version'),
    #============Ac
    path('customer_folder_delete/<entity_id>/<folder_id>/',customer_folder_delete,name="customer_folder_delete"),
    path('document_delete/<entity_id>/<folder_id>/<document_id>/', document_delete,name='document_delete'),
    path('aggrement_template_create/', aggrement_template_create,name='aggrement_template_create'),
    path('aggrement_template_list/', aggrement_template_list,name='aggrement_template_list'),
    path('aggrement_template_view/<template_id>/', aggrement_template_view,name='aggrement_template_view'),
    path('document_edit/<entity_id>/<folder_id>/', document_edit,name='document_edit'),


    path('audit_view', audit_view, name='audit_view'),
    path('document_list/', document_list, name='document_list'),
    path('customer_document_view/<pk>/',customer_document_view, name='customer_document_view'),
    path('loan_detail_trenches/<loanapp_id>/',loan_detail_trenches, name='loan_detail_trenches'),
    path('loan_upadate_trenches/<loanapp_id>/',loan_upadate_trenches, name='loan_upadate_trenches'),
    path('milestone_edit_v1/<loanapp_id>/',milestone_edit_v1, name='milestone_edit_v1'),
    path('milestone_activity_edit_v1/<loanapp_id>/',milestone_activity_edit_v1, name='milestone_activity_edit_v1'),
    path('milestone_activity_create_v1/<loanapp_id>/',milestone_activity_create_v1, name='milestone_activity_create_v1'),
    path('milestone_activity_delete_v1/<loanapp_id>/<activity_id>/',milestone_activity_delete_v1, name='milestone_activity_delete_v1'),
    path('milestone_delete_v1/<loanapp_id>/<milestone_id>/',milestone_delete_v1, name='milestone_delete_v1'),
    path('milestone_create_v1/<loanapp_id>/',milestone_create_v1, name='milestone_create_v1'),
    path('agreement_signature_update/<agreement_id>/',agreement_signature_update, name='agreement_signature_update'),
]