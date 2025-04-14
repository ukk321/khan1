from django import forms
from dal import autocomplete
from .models import SubServicesModel, ServiceModel, CategoryModel


class SubServicesAdminForm(forms.ModelForm):
    service = forms.ModelChoiceField(
        queryset=ServiceModel.objects.all(),
        label='Collection',
        widget=forms.Select()
    )
    category = forms.ModelChoiceField(
        queryset=CategoryModel.objects.all(),
        label='Category',
        widget=autocomplete.ModelSelect2(url='category-autocomplete',
                                         forward=('service',))
    )
    subservice = forms.ModelChoiceField(
        queryset=SubServicesModel.objects.all(),
        label='Product',
        widget=autocomplete.ModelSelect2(url='subservices-autocomplete',
                                         forward=('service', 'category')),
        required=False
    )

    class Meta:
        model = SubServicesModel
        fields = '__all__'
