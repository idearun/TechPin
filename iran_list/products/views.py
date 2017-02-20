from django.db.models import Count
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from oauth2client import client, crypt
from django.core import serializers
from django.forms import model_to_dict
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context_processors import csrf
from django.urls import reverse
import json
import collections
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from iran_list.settings import SITE_ADDRESS
from iran_list.products.forms import SignupForm, LoginForm, ChangePasswordForm, EditUserForm, ResetPasswordForm, \
    ProductForm, VersionForm, CommentForm, RateForm
from iran_list.products.models import ResetPasswordCode, Profile, Product, get_sentinel_user, Version, Comment, Rate, \
    Type, Category
from django.conf import settings
from iran_list.products.models import SocialLogin


def pack_data(request, data):
    data['user'] = request.user
    data['categories'] = Category.objects.all()
    data['site_address'] = SITE_ADDRESS
    if data['site_address'][-1] == '/':
        data['site_address'] = data['site_address'][:-1]
    data.update(csrf(request))
    return data


def home(request):
    products = Product.objects.filter(status="pub")

    new_product_form = ProductForm()

    type_object = None
    if 'type' in request.GET:
        type_slug = request.GET['type']
        type_object = get_object_or_404(Type, slug=type_slug)
        products = products.filter(product_type=type_object)

    category_object = None
    if 'category' in request.GET:
        category_slug = request.GET['category']
        category_object = get_object_or_404(Category, slug=category_slug)
        products = products.filter(categories=category_object)

    top_p_products = products.annotate(rate_count=Count('rates')).order_by("-rate_count")[:25]
    top_e_products = products.order_by("-average_p_rate")[:25]
    top_new_products = products.order_by("-created_at")[:25]
    top_ranked = products.order_by("-ranking")[:25]

    types = Type.objects.all()
    categories = Category.objects.all()

    data = pack_data(request, {'top_p_products': top_p_products, 'top_e_products': top_e_products,
                               'top_new_products': top_new_products, 'top_ranked': top_ranked, 'types': types,
                               'categories': categories, 'type': type_object, 'category': category_object,
                               'form': new_product_form})
    return render_to_response('home.html', data)


def all_products(request):
    products = Product.objects.filter(status="pub").order_by("name_en")
    products_dict = collections.OrderedDict()

    for product in products:
        if product.name_en[0] in [str(a) for a in range(0, 10)]:
            if "#" in products_dict:
                products_dict["#"].append(product)
            else:
                products_dict["#"] = [product]
        else:
            if product.name_en[0].upper() in products_dict:
                products_dict[product.name_en[0].upper()].append(product)
            else:
                products_dict[product.name_en[0].upper()] = [product]

    data = pack_data(request, {'products': collections.OrderedDict(sorted(products_dict.items()))})
    return render_to_response('products/all.html', data)


def signup(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('home'))

    signup_form = SignupForm()
    if request.method == 'POST':
        signup_form = SignupForm(request.POST)

        if signup_form.is_valid():
            user = signup_form.save()
            if user:
                data = {'message': _(u'Successfully Registered. You can login now.'),
                        'login': True}
                data.update(csrf(request))
                return render_to_response('common/message.html', data)

    data = {'form': signup_form, 'title': _(u'Join Iran List'), 'gp_client_id': settings.GOOGLE_OAUTH2_CLIENT_ID}
    data = pack_data(request, data)
    return render_to_response('users/signup.html', data)


def signin(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('home'))

    login_form = LoginForm()
    if request.method == 'POST':
        login_form = LoginForm(request.POST)

        if login_form.is_valid():
            user = login_form.user
            if user is not None:
                login(request, user)

                if Profile.objects.filter(user_id=user.id).count() == 0:
                    Profile.objects.create(user=user)

                return HttpResponseRedirect(reverse('home'))

    data = {'form': login_form, 'title': _(u'Enter Iran List'), 'gp_client_id': settings.GOOGLE_OAUTH2_CLIENT_ID }
    data = pack_data(request, data)
    return render_to_response('users/login.html', data)

def google_signin(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('home'))

    # (Receive token by HTTPS POST)
    token = request.POST.get("idtoken", "")
    data = {'success': True, 'user': True, 'token': token}
    try:
        idinfo = client.verify_id_token(token, settings.GOOGLE_OAUTH2_CLIENT_ID)

        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise crypt.AppIdentityError("Wrong issuer.")

        # If auth request is from a G Suite domain:
        #if idinfo['hd'] != GSUITE_DOMAIN_NAME:
        #    raise crypt.AppIdentityError("Wrong hosted domain.")
    except crypt.AppIdentityError:
        # Invalid token
        data['success'] = False

    userid = idinfo['sub']

    #check if user is not in the social login table then create it, else just log him in
    try:
        social_user = SocialLogin.objects.get(social_unique_id=userid)

    except SocialLogin.DoesNotExist:

        user = User(first_name=idinfo['given_name'], last_name=idinfo['family_name'], email=idinfo['email'],
                username=idinfo['email'], password=User.objects.make_random_password())
        user.save()

        try:
            social_user = SocialLogin(user=user, social_unique_id=userid)
            social_user.save()
        except:
            user.delete()

    if social_user is not None:
        user = User.objects.get(id=social_user.user_id)
        if user is not None:
            login(request, user)
            print(user.is_authenticated)
    else:
        data['success'] = False
        print( 'user none' )

    mimetype = 'application/json'
    return HttpResponse(json.dumps(data), mimetype)

@login_required
def change_password(request):
    password_form = ChangePasswordForm(request.user)
    if request.method == 'POST':
        password_form = ChangePasswordForm(request.user, data=request.POST)

        if password_form.is_valid():
            if password_form.save():
                data = {'message': _(u'Password Successfully changed!'), 'login': True}
                data.update(csrf(request))
                return render_to_response('common/message.html', data)

    data = {'password_form': password_form, 'title': _(u'Change Password')}
    data = pack_data(request, data)
    return render_to_response('users/change_password.html', data)


@login_required
def edit_profile(request):
    user = request.user
    user_form = EditUserForm(instance=user)
    if request.method == 'POST':
        user_form = EditUserForm(request.POST, instance=user)

        if user_form.is_valid():
            user_form.save()
            return HttpResponseRedirect(reverse('home'))

    data = {'user_form': user_form, 'title': _(u'Edit Profile')}
    data = pack_data(request, data)
    return render_to_response('users/edit_profile.html', data)


def request_reset(request):
    form = ResetPasswordForm()
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)

        if form.is_valid():
            sent = form.save()
            data = {'login': True}
            if not sent:
                data['message'] = _(u'Whoops! Something went wrong! Please Try again.')
            else:
                data['message'] = _(u'We Sent You an Email for Password Reset.')
            data.update(csrf(request))
            return render_to_response('common/message.html', data)

    data = {'form': form, 'page_header': _(u'Request Password Reset'), 'submit_name': _(u'Reset'),
            'title': _(u'Forgot Password')}
    data.update(csrf(request))
    data = pack_data(request, data)
    return render_to_response('users/forgot_password.html', data)


def reset_pass(request, reset_code):
    try:
        reset_code = ResetPasswordCode.objects.get(code=reset_code)
    except ResetPasswordCode.DoesNotExist:
        data = {'message': _(u'Invalid Link!'), 'login': True}
        data.update(csrf(request))
        return render_to_response('common/message.html', data)

    user = reset_code.profile.user

    password_form = ChangePasswordForm(user, reset=True)
    if request.method == 'POST':
        password_form = ChangePasswordForm(user, reset=True, data=request.POST)

        if password_form.is_valid():
            if password_form.save():
                reset_code.delete()
                data = {'message': _(u'Password Successfully changed!'), 'login': True}
                data.update(csrf(request))
                return render_to_response('common/message.html', data)

    data = {'password_form': password_form, 'title': _(u'Reset Password')}
    data = pack_data(request, data)
    return render_to_response('users/forgot_password.html', data)


def signout(request):
    logout(request)
    return HttpResponseRedirect(reverse('home'))


def add_product(request):
    form = ProductForm()

    if request.method == 'POST':
        product = Product()

        if request.user.is_authenticated:
            product.creator = Profile.get_user_profile(request.user)
        else:
            product.creator = Profile.get_user_profile(get_sentinel_user())

        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            product = form.save()
            if product:
                return HttpResponseRedirect(reverse('add_version', args=[product.id]))

    types = Type.objects.all()

    data = {'form': form, 'types': types}
    data = pack_data(request, data)
    return render_to_response('products/add.html', data)


def add_version(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if product.version is not None and not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    last_version = product.last_approved_version()
    if last_version:
        initial_data = model_to_dict(last_version)
    else:
        initial_data = {}
    form = VersionForm(initial_data)

    if request.method == "POST":
        version = Version()
        version.version_code = 0
        version.product = product
        if request.user.is_authenticated:
            version.editor = Profile.get_user_profile(request.user)
        else:
            version.editor = Profile.get_user_profile(get_sentinel_user())

        form = VersionForm(request.POST, request.FILES, instance=version)
        if form.is_valid():
            form.save()
            data = {'message': _(u'Successfully added your update. We will review and apply it asap!'), 'home': True}
            data.update(csrf(request))
            return render_to_response('common/message.html', data)

    data = {'form': form}
    data = pack_data(request, data)
    return render_to_response('products/add_version.html', data)


def product_page(request, slug):
    if slug.endswith("/"):
        slug = slug[:-1]

    product = get_object_or_404(Product, slug=slug, status="pub")
    version = product.last_approved_version()

    product.hit()

    comment_form = CommentForm()

    user_profile = None
    rate = None
    if request.user.is_authenticated:
        user_profile = Profile.get_user_profile(request.user)
        try:
            rate = Rate.objects.get(user_id=user_profile.id, product_id=product.id, user_type=user_profile.is_editor)
        except Rate.DoesNotExist:
            pass
        except Rate.MultipleObjectsReturned:
            rates = Rate.objects.filter(user_id=user_profile.id, product_id=product.id,
                                        user_type=user_profile.is_editor)
            rate = rates[0]
            for i in range(1, rates.count()):
                _rate = rates[i]
                _rate.delete()

    rate_form = RateForm(instance=rate)

    comments = product.comments.filter(status="pub")

    commented = False
    rated = False

    if request.method == "POST":
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('login'))

        if "rating" in request.POST:
            if rate is None:
                rate = Rate()
                user_profile = Profile.get_user_profile(request.user)
                rate.user = user_profile
                rate.user_type = user_profile.is_editor
                rate.product = product
            rate_form = RateForm(request.POST, instance=rate)
            if rate_form.is_valid():
                rate_form.save()
                commented = True

        elif "comment" in request.POST:
            comment = Comment()
            comment.user = Profile.get_user_profile(request.user)
            comment.product = product
            comment_form = CommentForm(request.POST, instance=comment)
            if comment_form.is_valid():
                comment_form.save()
                comment_form = CommentForm()
                commented = True

    data = {'product': product, 'version': version, 'rate_form': rate_form, 'comment_form': comment_form,
            'comments': comments, 'commented': commented, 'rated': rated}
    data = pack_data(request, data)
    return render_to_response('products/product_page.html', data)


def rate_product(request, product_slug):
    if product_slug.endswith("/"):
        product_slug = product_slug[:-1]

    data = {'success': False, 'user': True}

    if not request.user.is_authenticated():
        data['user'] = False

    elif request.is_ajax() and request.method == "POST":
        try:
            product = Product.objects.get(slug=product_slug, status="pub")
            user_profile = Profile.get_user_profile(request.user)
            try:
                rate = Rate.objects.get(user_id=user_profile.id, product_id=product.id,
                                        user_type=user_profile.is_editor)
            except Rate.MultipleObjectsReturned:
                rates = Rate.objects.filter(user_id=user_profile.id, product_id=product.id,
                                            user_type=user_profile.is_editor)
                rate = rates[0]
                for i in range(1, rates.count()):
                    _rate = rates[i]
                    _rate.delete()
            except Rate.DoesNotExist:
                rate = Rate()
                user_profile = Profile.get_user_profile(request.user)
                rate.user = user_profile
                rate.user_type = user_profile.is_editor
                rate.product = product
            rate_form = RateForm(request.POST, instance=rate)
            if rate_form.is_valid():
                rate_form.save()
                data['success'] = True

        except Product.DoesNotExist:
            pass

    mimetype = 'application/json'
    return HttpResponse(json.dumps(data), mimetype)


def about(request):
    data = pack_data(request, {'page_title': 'About'})
    return render_to_response('about.html', data)


def contribute(request):
    data = pack_data(request, {})
    return render_to_response('contribute.html', data)
