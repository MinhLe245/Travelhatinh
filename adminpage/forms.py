from django import forms
from app.models import Tour

class TourForm(forms.ModelForm):
    class Meta:
        model = Tour
        fields = ['name', 'describe', 'price', 'duration_days', 'start_date', 'image', 'code']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'describe': forms.Textarea(attrs={'rows': 4}),
        }
