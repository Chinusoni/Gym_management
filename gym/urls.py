from django.urls import path
from . import views

urlpatterns = [
    # Public
    path('', views.home, name='home'),

    # Auth
    path('admin-panel/login/', views.admin_login, name='admin_login'),
    path('admin-panel/logout/', views.admin_logout, name='admin_logout'),

    # Dashboard
    path('admin-panel/', views.dashboard, name='dashboard'),

    # Members
    path('admin-panel/members/', views.member_list, name='member_list'),
    path('admin-panel/members/add/', views.member_add, name='member_add'),
    path('admin-panel/members/<int:pk>/', views.member_detail, name='member_detail'),
    path('admin-panel/members/<int:pk>/edit/', views.member_edit, name='member_edit'),
    path('admin-panel/members/<int:pk>/delete/', views.member_delete, name='member_delete'),

    # Attendance
    path('admin-panel/attendance/', views.attendance, name='attendance'),
    path('admin-panel/attendance/<int:pk>/delete/', views.attendance_delete, name='attendance_delete'),

    # Payments
    path('admin-panel/payments/', views.payment_list, name='payment_list'),
    path('admin-panel/payments/add/', views.payment_add, name='payment_add'),
    path('admin-panel/payments/<int:pk>/delete/', views.payment_delete, name='payment_delete'),

    # Plans
    path('admin-panel/plans/', views.plan_list, name='plan_list'),
    path('admin-panel/plans/add/', views.plan_add, name='plan_add'),
    path('admin-panel/plans/<int:pk>/edit/', views.plan_edit, name='plan_edit'),

    # Settings
    path('admin-panel/settings/', views.gym_settings_view, name='gym_settings'),
]
