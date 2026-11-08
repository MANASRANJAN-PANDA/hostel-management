from django import forms
from .models import Room
from hostels.models import Hostel, Floor

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['hostel', 'floor', 'room_number', 'room_type', 'capacity', 'monthly_rent', 'room_status', 'description']
        widgets = {
            'hostel': forms.Select(attrs={'class': 'form-select', 'id': 'id_hostel'}),
            'floor': forms.Select(attrs={'class': 'form-select', 'id': 'id_floor'}),
            'room_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 101, A-202'}),
            'room_type': forms.Select(attrs={'class': 'form-select', 'id': 'id_room_type'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'id': 'id_capacity'}),
            'monthly_rent': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '₹ Monthly Rent'}),
            'room_status': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Room facilities, notes, etc.'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'hostel' in self.data:
            try:
                hostel_id = int(self.data.get('hostel'))
                self.fields['floor'].queryset = Floor.objects.filter(hostel_id=hostel_id).order_by('floor_number')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['floor'].queryset = self.instance.hostel.floors.order_by('floor_number')
