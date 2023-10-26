from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import UserLoginForm, CustomPasswordResetForm

auth_views.PasswordResetView.form_class = CustomPasswordResetForm

urlpatterns = [    
    path('', auth_views.LoginView.as_view(template_name='users/auth-login.html', authentication_form=UserLoginForm), name='login'),
	path('signup/', views.sign_up, name='signup'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/auth-logout.html'), name='logout'),
    path('account/', views.profile, name='profile'),
	path('account_activation_sent/', views.account_activation_sent, name='account_activation_sent'),
	path('activate/<uidb64>/<token>/', views.activate, name='activate'),
	path(
		'password-reset/',
		 auth_views.PasswordResetView.as_view(template_name='users/password_reset.html'),
		 name='password_reset'
		 ),

	path(
		'password-reset/done/',
		 auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'),
		 name='password_reset_done'
		 ),

	path(
		'password-reset-confirm/<uidb64>/<token>/',
		 auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'),
		 name='password_reset_confirm'
		 ),

	path(
		'password-reset-complete/',
		 auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'),
		 name='password_reset_complete'
		 ),
]