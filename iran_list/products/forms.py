import hashlib
from datetime import datetime
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Q
from django.forms import ModelForm, Form
from django.utils.translation import ugettext_lazy as _
from iran_list.products.mail import send_reset_pass_mail
from iran_list.products.models import Profile, ResetPasswordCode, Product, Version, Comment, Rate


class SignupForm(ModelForm):
    password = forms.CharField(max_length=32, widget=forms.PasswordInput, required=True, label=_(u'Password'))
    confirm_password = forms.CharField(max_length=32, widget=forms.PasswordInput, required=True,
                                       label=_(u'Confirm Password'))

    class Meta:
        model = User
        fields = ['first_name', 'email']

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].help_text = _("Full Name")

    def clean(self):

        password = self.cleaned_data.get('password', None)
        confirm_password = self.cleaned_data.get('confirm_password', None)

        if password and password != confirm_password:
            raise forms.ValidationError(_("Passwords Don't Match!"))

    def clean_password(self):
        password = self.cleaned_data.get('password', None)
        if len(password) < 8:
            raise forms.ValidationError(_("The new password must be at least 8 characters long!"))
        return password

    def clean_email(self):
        email = self.cleaned_data.get('email', None)
        if User.objects.filter(email__iexact=email).count() > 0:
            raise forms.ValidationError(_("This Email is Already in Use!"))
        return email

    def save(self, commit=True):
        user = super(SignupForm, self).save(commit)
        user.set_password(self.cleaned_data['password'])
        user.username = user.email.lower()
        user.save()

        profile = Profile(user=user)
        profile.save()

        return user


class LoginForm(Form):
    email = forms.CharField(max_length=30, required=True, label=_(u'Email'))
    password = forms.CharField(max_length=32, widget=forms.PasswordInput, required=True, label=_(u'Password'))

    def clean(self):
        cleaned_data = super(LoginForm, self).clean()

        try:
            email = cleaned_data['email'].lower()
            password = cleaned_data['password']
        except KeyError:
            raise forms.ValidationError(_("Please enter both Email and Password!"))

        try:
            username = User.objects.get(email__iexact=email).username
        except User.DoesNotExist:
            raise forms.ValidationError(_(u"Email or Password is Invalid!"))

        user = authenticate(username=username, password=password)

        if user is None:
            raise forms.ValidationError(_(u"Email or Password is Invalid!"))
        if not user.is_active:
            raise forms.ValidationError(u"This Account is not activated!")

        self.user = user


class ChangePasswordForm(Form):
    old_password = forms.CharField(widget=forms.PasswordInput, label=_(u"Current Password"))
    new_password = forms.CharField(widget=forms.PasswordInput, label=_(u"New Password"))
    confirm_password = forms.CharField(widget=forms.PasswordInput, label=_(u"Confirm Password"))

    def __init__(self, user, reset=False, *args, **kwargs):
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

        # if this form is being used to reset forgotten password, we won't ask for the old password
        self.reset = reset
        if self.reset:
            del (self.fields['old_password'])

        self.user = user

    def clean_old_password(self):
        password = self.cleaned_data['old_password']
        user = authenticate(username=self.user.username, password=password)
        if user is None:
            raise forms.ValidationError(_(u"Old Password is Invalid!"))
        return password

    def clean_new_password(self):
        password = self.cleaned_data.get('new_password', None)
        if len(password) < 8:
            raise forms.ValidationError(_("New password must be at least 8 characters long!"))
        return password

    def clean(self):
        password = self.cleaned_data.get('new_password', None)
        confirm_password = self.cleaned_data.get('confirm_password', None)

        if password and password != confirm_password:
            raise forms.ValidationError(_("Passwords Don't Match!"))

    def save(self):
        try:
            user = self.user
            user.set_password(self.cleaned_data['new_password'])
            user.save()

        except User.DoesNotExist:
            return False

        return True


class EditUserForm(ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'email']

    def __init__(self, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)

        self.fields['first_name'].help_text = _("Full Name")

        self.email = None
        if self.instance.email:
            self.email = self.instance.email

        self.user_id = -1
        if self.instance.id:
            self.user_id = self.instance.id

    def clean_email(self):
        email = self.cleaned_data.get('email', None)
        if User.objects.filter(email__iexact=email).exclude(id=self.user_id).count() > 0:
            raise forms.ValidationError(_("This Email is Already in Use!"))
        return email

    def save(self, commit=True):
        user = super(EditUserForm, self).save(commit)

        user.username = user.username.lower()
        user.save()

        return user


class ResetPasswordForm(Form):
    email = forms.EmailField(label=_("Your Email"))

    def save(self):
        email = self.cleaned_data['email']
        try:
            user = User.objects.get(email=email)
            profile = user.profile
        except:
            user = None
            profile = None

        if user and profile:
            hasher = hashlib.sha1()
            username_str = user.username.encode('utf-8')
            datetime_str = str(datetime.now()).encode('utf-8')
            hasher.update(username_str + datetime_str)
            hashed = hasher.hexdigest()[:64]
            reset_pass = ResetPasswordCode()
            reset_pass.profile = profile
            reset_pass.code = hashed
            reset_pass.save()
            try:
                send_reset_pass_mail(email, user.get_full_name(), hashed)
                return True
            except:
                reset_pass.delete()

        return False


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ['name_en', 'website', 'product_type', 'categories']


class VersionForm(ModelForm):
    class Meta:
        model = Version
        fields = ['description_en', 'email', 'android_app', 'ios_app', 'linkedin', 'twitter', 'instagram', 'extra_url',
                  'year', 'city', 'country', 'employees', 'logo', 'banner']


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text']


class RateForm(ModelForm):
    class Meta:
        model = Rate
        fields = ['rate']
