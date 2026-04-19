from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Sum, Q
from datetime import date, timedelta
from .models import Member, MembershipPlan, Attendance, Payment, GymSettings
from .forms import (MemberForm, MembershipPlanForm, PaymentForm,
                    AttendanceForm, QuickCheckinForm, GymSettingsForm)


# ── Public ──────────────────────────────────────────────────────────────────

def home(request):
    return render(request, 'gym/home.html')


# ── Auth ─────────────────────────────────────────────────────────────────────

def admin_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, 'Invalid username or password.')
    return render(request, 'gym/login.html')


def admin_logout(request):
    logout(request)
    return redirect('home')


# ── Dashboard ────────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    today = date.today()
    week_ago = today - timedelta(days=7)

    total_members = Member.objects.count()
    active_members = Member.objects.filter(status='active').count()
    expired_members = Member.objects.filter(status='expired').count()
    today_checkins = Attendance.objects.filter(date=today).count()

    expiring_soon = Member.objects.filter(
        plan_end_date__gte=today,
        plan_end_date__lte=today + timedelta(days=7),
        status='active'
    ).order_by('plan_end_date')[:5]

    recent_checkins = Attendance.objects.select_related('member').filter(
        date=today
    ).order_by('-check_in_time')[:10]

    overdue_payments = Payment.objects.filter(status='overdue').count()

    month_revenue = Payment.objects.filter(
        payment_date__year=today.year,
        payment_date__month=today.month,
        status='paid'
    ).aggregate(total=Sum('amount'))['total'] or 0

    inactive_members = Member.objects.filter(
        status='active'
    ).exclude(
        attendances__date__gte=week_ago
    )[:5]

    context = {
        'total_members': total_members,
        'active_members': active_members,
        'expired_members': expired_members,
        'today_checkins': today_checkins,
        'expiring_soon': expiring_soon,
        'recent_checkins': recent_checkins,
        'overdue_payments': overdue_payments,
        'month_revenue': month_revenue,
        'inactive_members': inactive_members,
        'today': today,
    }
    return render(request, 'gym/dashboard.html', context)


# ── Members ───────────────────────────────────────────────────────────────────

@login_required
def member_list(request):
    q = request.GET.get('q', '')
    status = request.GET.get('status', '')
    members = Member.objects.select_related('membership_plan').all()
    if q:
        members = members.filter(
            Q(first_name__icontains=q) | Q(last_name__icontains=q) |
            Q(phone__icontains=q) | Q(email__icontains=q)
        )
    if status:
        members = members.filter(status=status)
    context = {'members': members, 'q': q, 'status': status,
               'total': members.count()}
    return render(request, 'gym/members/list.html', context)


@login_required
def member_add(request):
    if request.method == 'POST':
        form = MemberForm(request.POST, request.FILES)
        if form.is_valid():
            member = form.save()
            messages.success(request, f'Member {member.full_name} added successfully!')
            return redirect('member_detail', pk=member.pk)
    else:
        form = MemberForm(initial={'join_date': date.today(), 'plan_start_date': date.today()})
    plans = MembershipPlan.objects.filter(is_active=True)
    return render(request, 'gym/members/form.html', {'form': form, 'plans': plans, 'title': 'Add Member'})


@login_required
def member_edit(request, pk):
    member = get_object_or_404(Member, pk=pk)
    if request.method == 'POST':
        form = MemberForm(request.POST, request.FILES, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, 'Member updated successfully!')
            return redirect('member_detail', pk=pk)
    else:
        form = MemberForm(instance=member)
    plans = MembershipPlan.objects.filter(is_active=True)
    return render(request, 'gym/members/form.html', {'form': form, 'plans': plans, 'title': 'Edit Member', 'member': member})


@login_required
def member_detail(request, pk):
    member = get_object_or_404(Member, pk=pk)
    attendances = member.attendances.order_by('-date')[:30]
    payments = member.payments.order_by('-payment_date')[:10]
    total_visits = member.attendances.count()
    this_month_visits = member.attendances.filter(
        date__year=date.today().year,
        date__month=date.today().month
    ).count()
    context = {
        'member': member,
        'attendances': attendances,
        'payments': payments,
        'total_visits': total_visits,
        'this_month_visits': this_month_visits,
    }
    return render(request, 'gym/members/detail.html', context)


@login_required
def member_delete(request, pk):
    member = get_object_or_404(Member, pk=pk)
    if request.method == 'POST':
        name = member.full_name
        member.delete()
        messages.success(request, f'{name} has been removed.')
        return redirect('member_list')
    return render(request, 'gym/members/confirm_delete.html', {'member': member})


# ── Attendance ────────────────────────────────────────────────────────────────

@login_required
def attendance(request):
    today = date.today()
    selected_date = request.GET.get('date', str(today))
    try:
        from datetime import datetime
        sel_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
    except ValueError:
        sel_date = today

    records = Attendance.objects.filter(date=sel_date).select_related('member').order_by('-check_in_time')
    checkin_form = QuickCheckinForm()

    if request.method == 'POST':
        checkin_form = QuickCheckinForm(request.POST)
        if checkin_form.is_valid():
            member = checkin_form.cleaned_data['member']
            attendance_obj, created = Attendance.objects.get_or_create(
                member=member,
                date=today,
                defaults={'check_in_time': timezone.now().time()}
            )
            if created:
                messages.success(request, f'✅ {member.full_name} checked in!')
            else:
                messages.warning(request, f'{member.full_name} already checked in today.')
            return redirect('attendance')

    context = {
        'records': records,
        'checkin_form': checkin_form,
        'selected_date': sel_date,
        'today': today,
        'count': records.count(),
    }
    return render(request, 'gym/attendance/index.html', context)


@login_required
def attendance_delete(request, pk):
    record = get_object_or_404(Attendance, pk=pk)
    if request.method == 'POST':
        record.delete()
        messages.success(request, 'Attendance record removed.')
    return redirect('attendance')


# ── Payments ──────────────────────────────────────────────────────────────────

@login_required
def payment_list(request):
    today = date.today()
    status = request.GET.get('status', '')
    payments = Payment.objects.select_related('member', 'plan').all()
    if status:
        payments = payments.filter(status=status)

    total_paid = Payment.objects.filter(status='paid').aggregate(t=Sum('amount'))['t'] or 0
    month_paid = Payment.objects.filter(
        status='paid', payment_date__year=today.year, payment_date__month=today.month
    ).aggregate(t=Sum('amount'))['t'] or 0
    pending_count = Payment.objects.filter(status='pending').count()

    context = {
        'payments': payments,
        'status': status,
        'total_paid': total_paid,
        'month_paid': month_paid,
        'pending_count': pending_count,
    }
    return render(request, 'gym/payments/list.html', context)


@login_required
def payment_add(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Payment recorded!')
            return redirect('payment_list')
    else:
        form = PaymentForm(initial={'payment_date': date.today()})
    return render(request, 'gym/payments/form.html', {'form': form, 'title': 'Record Payment'})


@login_required
def payment_delete(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    if request.method == 'POST':
        payment.delete()
        messages.success(request, 'Payment deleted.')
    return redirect('payment_list')


# ── Plans ─────────────────────────────────────────────────────────────────────

@login_required
def plan_list(request):
    plans = MembershipPlan.objects.annotate(member_count=Count('member')).all()
    return render(request, 'gym/plans/list.html', {'plans': plans})


@login_required
def plan_add(request):
    if request.method == 'POST':
        form = MembershipPlanForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Plan created!')
            return redirect('plan_list')
    else:
        form = MembershipPlanForm()
    return render(request, 'gym/plans/form.html', {'form': form, 'title': 'Add Plan'})


@login_required
def plan_edit(request, pk):
    plan = get_object_or_404(MembershipPlan, pk=pk)
    if request.method == 'POST':
        form = MembershipPlanForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()
            messages.success(request, 'Plan updated!')
            return redirect('plan_list')
    else:
        form = MembershipPlanForm(instance=plan)
    return render(request, 'gym/plans/form.html', {'form': form, 'title': 'Edit Plan', 'plan': plan})


# ── Settings ──────────────────────────────────────────────────────────────────

@login_required
def gym_settings_view(request):
    try:
        settings_obj = GymSettings.objects.get(pk=1)
    except GymSettings.DoesNotExist:
        settings_obj = GymSettings()

    if request.method == 'POST':
        form = GymSettingsForm(request.POST, instance=settings_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Gym settings updated!')
            return redirect('gym_settings')
    else:
        form = GymSettingsForm(instance=settings_obj)
    return render(request, 'gym/settings.html', {'form': form})
