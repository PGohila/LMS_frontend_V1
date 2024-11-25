from django import forms 

class ValueChainSetupForm(forms.Form):
    status = forms.BooleanField(required=False,widget=forms.CheckboxInput(attrs={"class": "form-check-input"}))
    valuechain_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
    max_amount = forms.FloatField(required=True,label='Maximum Amount', widget=forms.NumberInput(attrs={"class": "form-control"}))
    min_amount = forms.FloatField(required=True,label='Minimum Amount', widget=forms.NumberInput(attrs={"class": "form-control"}))
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))

class mileStoneSetupForm(forms.Form):
    status = forms.BooleanField(required=False,widget=forms.CheckboxInput(attrs={"class": "form-check-input"}))
    milestone_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
    max_amount = forms.FloatField(required=True,label='Maximum Amount', widget=forms.NumberInput(attrs={"class": "form-control"}))
    min_amount = forms.FloatField(required=True,label='Minimum Amount', widget=forms.NumberInput(attrs={"class": "form-control"}))
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))

class MilestoneStageForm(forms.Form):
 
    stage_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
    max_amount = forms.FloatField(required=True,label='Maximum Amount', widget=forms.NumberInput(attrs={"class": "form-control"}))
    min_amount = forms.FloatField(required=True,label='Minimum Amount', widget=forms.NumberInput(attrs={"class": "form-control"}))
    sequence = forms.IntegerField(
        required=True,
        label='Sequence',
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))
