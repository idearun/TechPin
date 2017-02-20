from django.conf.urls import url
from .views import signin, signup, signout, edit_profile, change_password, home, request_reset, reset_pass, add_product, \
    add_version, product_page, all_products, about, contribute, rate_product, google_signin

urlpatterns = [
    url(r'^signup/?$', signup, name='signup'),
    url(r'^login/?$', signin, name='login'),
    url(r'^google-login/?$', google_signin, name='google-login'),
    url(r'^logout/?$', signout, name='logout'),

    url(r'^change-password/?$', change_password, name='change_password'),
    url(r'^edit-profile/?$', edit_profile, name='edit_profile'),

    url(r'^reset-password/([0-9a-f]+)/?$', reset_pass, name='reset_pass'),
    url(r'^forgot-password/?$', request_reset, name='forgot_pass'),

    url(r'^products/add/?$', add_product, name='add_product'),
    url(r'^products/(\d+)/versions/add$', add_version, name='add_version'),
    url(r'^products/rate/(.+)?/$', rate_product, name='rate_product'),

    url(r'^all/?$', all_products, name='all_products'),

    url(r'^about/?$', about, name='about'),
    url(r'^contribute/?$', contribute, name='contribute'),

    url(r'^$', home, name='home'),

    url(r'^(.+)/?$', product_page, name='product_page'),

]
