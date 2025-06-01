from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.panel_index_view, name='panel_index'), # Index for the panel app
    path('register/', views.register, name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('hosting-plans/', views.list_hosting_plans_view, name='list_hosting_plans'),
    path('order-hosting/<int:plan_id>/', views.order_hosting_plan_view, name='order_hosting_plan'),
    path('order-success/', views.order_success_view, name='order_success'),
    path('my-services/', views.customer_services_view, name='customer_services'),

    # Password Change URLs
    path('password_change/',
         auth_views.PasswordChangeView.as_view(
             template_name='panel/password_change_form.html',
             success_url='/panel/password_change/done/' # Note: success_url ideally uses reverse lazy
         ),
         name='password_change'),
    path('password_change/done/',
         auth_views.PasswordChangeDoneView.as_view(
             template_name='panel/password_change_done.html'
         ),
         name='password_change_done'),
]
