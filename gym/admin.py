from django.contrib import admin
from .models import GymSettings, Member, MembershipPlan, Attendance, Payment

admin.site.register(GymSettings)
admin.site.register(Member)
admin.site.register(MembershipPlan)
admin.site.register(Attendance)
admin.site.register(Payment)
