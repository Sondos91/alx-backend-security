from django.urls import path
from . import views

app_name = 'ip_tracking'

urlpatterns = [
    path('test/', views.test_view, name='test'),
    path('logs/', views.logs_view, name='logs'),
    path('login/', views.login_view, name='login_view'),
    path('logout/', views.logout_view, name='logout_view'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('sensitive-data/', views.sensitive_data_view, name='sensitive_data'),
]
