from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib import messages
from .forms import UserSignupForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token

def sign_up(request):
    if request.method == 'POST':
        form = UserSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            subject = 'Activate Your HRVSciHub Account'
            message = render_to_string('users/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
				'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject, message)
            return redirect('account_activation_sent')
    else:
        form = UserSignupForm()
    return render(request, 'users/auth-register.html', {'form' : form})


def account_activation_sent(request):
	return render(request, 'users/account_activation_sent.html')


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64).decode())
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.profile.email_confirmed = True
        user.save()
        auth_login(request, user)
        return redirect('subject_list')
    else:
        return render(request, 'users/account_activation_invalid.html')


@login_required
def profile(request):
	if request.method == 'POST':
		u_form = UserUpdateForm(request.POST, instance=request.user)
		p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
		if u_form.is_valid() and p_form.is_valid():
			u_form.save()
			p_form.save()
			messages.info(request, f'Your Profile has been Updated')
			return redirect('profile')
	if 'btn_delete' in request.POST and request.method == "POST":
		user=request.user
		user.delete()
		return redirect('login')
	u_form = UserUpdateForm(instance=request.user)
	p_form = ProfileUpdateForm(instance=request.user.profile)
	context = {
		'u_form':u_form,
		'p_form':p_form
	}
	return render(request, 'users/profile.html', context)