from django import forms

from .models import PaymentModel, BookingModel


class PaymentModelForm(forms.ModelForm):
    class Meta:
        model = PaymentModel
        fields = '__all__'  # Include all fields or specify particular fields as needed

    booking = forms.ModelChoiceField(
        queryset=BookingModel.objects.all(),
        widget=forms.Select(attrs={
            'style': 'width: 100%; max-width: 400px; box-sizing: border-box; '
                     'overflow: hidden; text-overflow: ellipsis; white-space: nowrap;'
        }),
    )
