from django import forms
from django.utils import timezone
from .models import RoomAllocation
from students.models import StudentProfile
from rooms.models import Room

class RoomAllocationForm(forms.ModelForm):
    student = forms.ModelChoiceField(
        queryset=StudentProfile.objects.filter(account_status='ACTIVE').select_related('user'),
        widget=forms.Select(attrs={'class': 'form-select select2'}),
        help_text="Only active approved students without active allocations"
    )
    room = forms.ModelChoiceField(
        queryset=Room.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select select2'}),
        help_text="Select an available room"
    )

    class Meta:
        model = RoomAllocation
        fields = ['student', 'room', 'allocation_date', 'notes']
        widgets = {
            'allocation_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Optional allocation notes / remarks'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['allocation_date'].initial = timezone.now().date()
        # Find students who do not have an active room allocation
        allocated_student_ids = RoomAllocation.objects.filter(status='ACTIVE').values_list('student_id', flat=True)
        self.fields['student'].queryset = StudentProfile.objects.filter(
            account_status='ACTIVE'
        ).exclude(id__in=allocated_student_ids).select_related('user')

        # Find rooms that have remaining capacity
        available_rooms = [r.pk for r in Room.objects.exclude(room_status='MAINTENANCE') if r.available_beds > 0]
        self.fields['room'].queryset = Room.objects.filter(pk__in=available_rooms).select_related('hostel')


class RoomTransferForm(forms.Form):
    new_room = forms.ModelChoiceField(
        queryset=Room.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select select2'}),
        label="Transfer to New Room"
    )
    transfer_date = forms.DateField(
        initial=timezone.now().date,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label="Transfer Effective Date"
    )
    reason = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Reason for room transfer'}),
        label="Reason for Transfer"
    )

    def __init__(self, current_room=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        available_rooms = [r.pk for r in Room.objects.exclude(room_status='MAINTENANCE') if r.available_beds > 0]
        if current_room:
            # exclude current room
            available_rooms = [pk for pk in available_rooms if pk != current_room.pk]
        self.fields['new_room'].queryset = Room.objects.filter(pk__in=available_rooms).select_related('hostel')


class RoomVacateForm(forms.Form):
    vacate_date = forms.DateField(
        initial=timezone.now().date,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label="Vacating Date"
    )
    remarks = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Check-out notes, clearance confirmation, key handover remarks, etc.'}),
        label="Vacating Remarks & Clearance"
    )
