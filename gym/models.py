from django.db import models
from django.utils import timezone
from datetime import date


class GymSettings(models.Model):
    gym_name = models.CharField(max_length=100, default='Iron Forge Gym')
    owner_name = models.CharField(max_length=100, default='Owner')
    phone_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    tagline = models.CharField(max_length=200, default='Forge Your Legacy')
    established_year = models.IntegerField(default=2024)

    class Meta:
        verbose_name = 'Gym Settings'

    def __str__(self):
        return self.gym_name

    def save(self, *args, **kwargs):
        self.pk = 1  # Singleton
        super().save(*args, **kwargs)


class MembershipPlan(models.Model):
    name = models.CharField(max_length=100)
    duration_months = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.duration_months}mo — ₹{self.price})"


class Member(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('inactive', 'Inactive'),
    ]

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    photo = models.ImageField(upload_to='member_photos/', blank=True, null=True)
    join_date = models.DateField(default=date.today)
    membership_plan = models.ForeignKey(MembershipPlan, on_delete=models.SET_NULL, null=True, blank=True)
    plan_start_date = models.DateField(null=True, blank=True)
    plan_end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def days_until_expiry(self):
        if self.plan_end_date:
            delta = self.plan_end_date - date.today()
            return delta.days
        return None

    @property
    def is_expiring_soon(self):
        days = self.days_until_expiry
        return days is not None and 0 <= days <= 7

    def update_status(self):
        if self.plan_end_date:
            if self.plan_end_date < date.today():
                self.status = 'expired'
            else:
                self.status = 'active'
            self.save()


class Attendance(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField(default=date.today)
    check_in_time = models.TimeField(default=timezone.now)
    notes = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['-date', '-check_in_time']
        unique_together = ['member', 'date']

    def __str__(self):
        return f"{self.member.full_name} — {self.date}"


class Payment(models.Model):
    STATUS_CHOICES = [
        ('paid', 'Paid'),
        ('pending', 'Pending'),
        ('overdue', 'Overdue'),
    ]

    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='payments')
    plan = models.ForeignKey(MembershipPlan, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    payment_date = models.DateField(default=date.today)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='paid')
    notes = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-payment_date']

    def __str__(self):
        return f"{self.member.full_name} — ₹{self.amount} ({self.status})"
