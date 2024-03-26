from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from django.contrib.auth.models import User
from django_countries.fields import CountryField
from .models import Profile

# custom reset password email
from email.mime.image import MIMEImage
from typing import Dict, Final, Optional

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator, PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.staticfiles import finders
from django.core.handlers.wsgi import WSGIRequest
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


class UserSignupForm(UserCreationForm):
	username = forms.CharField(label='',widget=forms.TextInput(attrs={'class': 'form-control'}))
	email = forms.EmailField(label='',widget=forms.TextInput(attrs={'class': 'form-control'}))
	password1 = forms.CharField(label='',widget=forms.PasswordInput(attrs={'class': 'form-control'}))
	password2 = forms.CharField(label='',widget=forms.PasswordInput(attrs={'class': 'form-control'}))
	class Meta:
		model = User
		fields = ['username','email','password1','password2']


class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)

    username = forms.CharField(label='',widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='',widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class UserUpdateForm(forms.ModelForm):
	username = forms.CharField(label='',widget=forms.TextInput(attrs={
		'class': 'form-control',
		'id':'inputUsername',
		'placeholder':'Username'
		}))
	email = forms.EmailField(label='', help_text='Required. Inform a valid email address.',widget=forms.TextInput(attrs={
		'class': 'form-control',
		'id':'inputEmail',
		'placeholder':'Email'
		}))	
	class Meta:
		model = User
		fields = ['username','email']

class ProfileUpdateForm(forms.ModelForm):
	first_name = forms.CharField(required=False, label='',widget=forms.TextInput(attrs={
		'class': 'form-control',
		'placeholder':'First name'
		}))
	last_name = forms.CharField(required=False, label='',widget=forms.TextInput(attrs={
		'class': 'form-control',
		'placeholder':'Last name'
		}))
	address = forms.CharField(required=False, label='',widget=forms.TextInput(attrs={
		'class': 'form-control',
		'placeholder':'1234 Main St'
		}))
	address2 = forms.CharField(required=False, label='',widget=forms.TextInput(attrs={
		'class': 'form-control',
		'placeholder':'Apartment, studio, or floor'
		}))
	city = forms.CharField(required=False, label='',widget=forms.TextInput(attrs={
		'class': 'form-control',
		}))
	image = forms.ImageField(widget=forms.FileInput(attrs={
		'name':'image',
		'accept':'image/*',
		'class':'form-control d-none',
		'id':'id_image',
		'onchange':'submitFunc()'
	}))
	country = CountryField(blank=True, blank_label='(Select country)').formfield(label='')
	class Meta:
		model = Profile
		fields = ['image','first_name','last_name','city','address','address2','country']


# Constants for sending password-reset emails.
LOGO_FILE_PATH: Final[str] = "assets/images/logo_email.png"
LOGO_CID_NAME: Final[str] = "logo"
PASSWORD_RESET_FORM_TEMPLATE: Final[str] = "users/password_reset.html"
PASSWORD_RESET_HTML_TEMPLATE: Final[str] = "users/password_reset_email.html"
PASSWORD_RESET_TEXT_TEMPLATE: Final[str] = "users/password_reset_email.txt"
PASSWORD_RESET_SUBJECT_TEMPLATE: Final[str] = "users/password_reset_subject.txt"
SUPPORT_EMAIL: Final[str] = " hrvscihub@gmail.com"
FROM_EMAIL: Final[str] = f"HRVSciHub Support <{SUPPORT_EMAIL}>"


def get_as_mime_image(image_file_path: str, cid_name: str) -> MIMEImage:
    """Fetch an image file and return it wrapped in a ``MIMEImage`` object for use 
    in emails.

    After the ``MIMEImage`` has been attached to an email, reference the image in 
    the HTML using the Content ID.

    Example:

    If the CID name is "logo", then the HTML reference would be:

    <img src="cid:logo" />

    Args:
        image_file_path: The path of the image. The path must be findable by the 
            Django staticfiles app.
        cid_name: The Content-ID name to use within the HTML email body to 
            reference the image.

    Raises:
        FileNotFoundError: If the image file cannot be found by the staticfiles app.

    Returns:
        MIMEImage: The image wrapped in a ``MIMEImage`` object and the Content ID 
        set to ``cid_name``.
    """
    paths = finders.find(image_file_path)
    if paths is None:
        raise FileNotFoundError(f"{image_file_path} not found in static files")

    if isinstance(paths, list):
        final_path = paths[0]
    else:
        final_path = paths
    with open(final_path, 'rb') as f:
        image_data = f.read()

    mime_image = MIMEImage(image_data)
    mime_image.add_header("Content-ID", f"<{cid_name}>")
    return mime_image


class CustomPasswordResetForm(PasswordResetForm):
    """Override the default Django password-reset form to send the password reset email using both HTML and plain text.
    """
    def send_mail(
        self,
        subject_template_name: str,
        email_template_name: str,
        context: Dict[str, str],
        from_email: Optional[str],
        to_email: str,
        html_email_template_name: Optional[str] = None,
    ) -> None:
        """Send a ``django.core.mail.EmailMultiAlternatives`` to ``to_email``.

        This method also attaches the company logo, which can be added to the 
        email HTML template using:

        <img src="cid:logo" />

        Args:
            subject_template_name: Path of the template to use as the email 
                subject.
            email_template_name: Path of the template to use for the plain text 
                email body.
            context: A context dictionary to use when rendering the password reset 
                email templates.
            from_email: The From email address.
            to_email: The To email address.
            html_email_template_name: Optional; Path of the template to use for 
                the HTML email body. Defaults to None.
        """
        subject = loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)

        email_message = EmailMultiAlternatives(subject, body, 
                                               from_email=from_email, to=[to_email],
                                               reply_to=[from_email])
        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name, context)
            email_message.attach_alternative(html_email, 'text/html')
            email_message.mixed_subtype = "related"
            mime_image = get_as_mime_image(image_file_path=LOGO_FILE_PATH, cid_name=LOGO_CID_NAME)
            email_message.attach(mime_image)  # type: ignore

        email_message.send()

    def save(
        self,
        domain_override: Optional[str] = None,
        subject_template_name: str = PASSWORD_RESET_SUBJECT_TEMPLATE,
        email_template_name: str = PASSWORD_RESET_TEXT_TEMPLATE,
        use_https: Optional[bool] = None,
        token_generator: PasswordResetTokenGenerator = default_token_generator,
        from_email: Optional[str] = FROM_EMAIL,
        request: Optional[WSGIRequest] = None,
        html_email_template_name: Optional[str] = PASSWORD_RESET_HTML_TEMPLATE,
        extra_email_context: Optional[Dict[str, str]] = None
    ) -> None:
        """Generate a one-use only link for resetting password and email it to 
        the user.

        Args:
            domain_override: Optional; Domain name to use in the email message 
                template that overrides the actual domain from which the email is 
                sent. Defaults to None.
            subject_template_name: Optional; Warning: this argument is overridden 
                by the global variable ``PASSWORD_RESET_SUBJECT_TEMPLATE``.
            email_template_name: Optional; Warning: this argument is overridden by 
                the global variable ``PASSWORD_RESET_TEXT_TEMPLATE``.
            use_https: Optional; If True, use HTTPS, otherwise use HTTP. Defaults 
                to False. Note that if the password reset HTTP request is received 
                via HTTPS, `use_https` will be set to True by the auth view.
            token_generator: Optional; Strategy object used to generate and check 
                tokens for the password reset mechanism. Defaults to an instance 
                of ``django.contrib.auth.tokens.PasswordResetTokenGenerator``.
            from_email: Optional; Warning: this argument is overridden by the 
                global variable``FROM_EMAIL``.
            request: Optional; The HttpRequest object. Defaults to None.
            html_email_template_name: Warning: this argument is overridden by the 
                global variable ``PASSWORD_RESET_HTML_TEMPLATE``.
            extra_email_context: Optional; Key-value pairs to add to the context 
                dictionary used to render the password reset email templates. 
                    Defaults to None.
        """
        email_template_name = PASSWORD_RESET_TEXT_TEMPLATE
        from_email = FROM_EMAIL
        html_email_template_name = PASSWORD_RESET_HTML_TEMPLATE
        subject_template_name = PASSWORD_RESET_SUBJECT_TEMPLATE

        email = self.cleaned_data["email"]
        if not domain_override:
            current_site = get_current_site(request)
            site_name = current_site.name
            domain = current_site.domain
        else:
            site_name = domain = domain_override
        UserModel = get_user_model()
        email_field_name = UserModel.get_email_field_name()  # type: ignore

        for user in self.get_users(email):
            user_email = getattr(user, email_field_name)
            context = {
                'email': user_email,
                'domain': domain,
                'site_name': site_name,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': 'https' if use_https else 'http',
                **(extra_email_context or {}),
            }

            self.send_mail(
                subject_template_name = subject_template_name,
                email_template_name = email_template_name,
                context = context,
                from_email = from_email,
                to_email = user_email,
                html_email_template_name = html_email_template_name
            )