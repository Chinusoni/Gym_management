from django import forms
from .models import Member, MembershipPlan, Payment, Attendance, GymSettings
from datetime import date
from dateutil.relativedelta import relativedelta


class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['first_name', 'last_name', 'phone', 'email', 'photo',
                  'join_date', 'membership_plan', 'plan_start_date', 'notes']
        widgets = {
            'join_date': forms.DateInput(attrs={'type': 'date'}),
            'plan_start_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def save(self, commit=True):
        member = super().save(commit=False)
        if member.membership_plan and member.plan_start_date:
            from dateutil.relativedelta import relativedelta
            member.plan_end_date = member.plan_start_date + relativedelta(
                months=member.membership_plan.duration_months
            )
            if member.plan_end_date >= date.today():
                member.status = 'active'
            else:
                member.status = 'expired'
        if commit:
            member.save()
        return member


class MembershipPlanForm(forms.ModelForm):
    class Meta:
        model = MembershipPlan
        fields = ['name', 'duration_months', 'price', 'description', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['member', 'plan', 'amount', 'payment_date', 'due_date', 'status', 'notes']
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['member', 'date', 'check_in_time', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'check_in_time': forms.TimeInput(attrs={'type': 'time'}),
        }


class QuickCheckinForm(forms.Form):
    member = forms.ModelChoiceField(
        queryset=Member.objects.filter(status='active'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Select Member'
    )


class GymSettingsForm(forms.ModelForm):
    class Meta:
        model = GymSettings
        fields = ['gym_name', 'owner_name', 'phone_number', 'email', 'address',
                  'tagline', 'established_year']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }
