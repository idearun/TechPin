from random import random
import math
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Avg
from django.utils.translation import ugettext_lazy as _
from iran_list.products.helper import DataField


class Profile(models.Model):
    twitter_handler = models.CharField(max_length=255, blank=True, null=True)
    auth_code = models.CharField(max_length=255, blank=True, null=True)

    is_editor = models.BooleanField(default=False, verbose_name=_(u"Is Editor"))
    user_point = models.PositiveIntegerField(default=0, verbose_name=_(u"User Points"))

    user = models.OneToOneField(User, related_name="profile", verbose_name=_(u"User"))

    def __str__(self):
        return self.user.get_full_name()

    @staticmethod
    def get_user_profile(user):
        try:
            return Profile.objects.get(user_id=user.id)
        except Profile.DoesNotExist:
            return Profile.objects.create(user=user)


class ResetPasswordCode(models.Model):
    profile = models.ForeignKey('Profile', related_name='reset_password_cods')
    creation_date = models.DateTimeField(auto_now=True)
    code = models.CharField(max_length=100, unique=True)


def get_sentinel_user():
    return User.objects.filter(is_superuser=True).first()


class Type(models.Model):
    name = models.CharField(max_length=50, verbose_name=_('English Name'))
    fa_name = models.CharField(max_length=50, verbose_name=_('Persian Name'))
    slug = models.SlugField(max_length=50, verbose_name=_(u"Slug"), unique=True)

    class Meta:
        verbose_name = _(u'Type')
        verbose_name_plural = _(u'Types')

    def __str__(self):
        return self.name


class Category(models.Model):
    name_en = models.CharField(max_length=50, verbose_name=_('English Name'))
    name_fa = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('Persian Name'))
    slug = models.SlugField(max_length=50, verbose_name=_(u"Slug"), unique=True)

    class Meta:
        verbose_name = _(u'Category')
        verbose_name_plural = _(u'Categories')

    def __str__(self):
        return self.name_en


class Product(models.Model):
    STATUS = (('pen', _(u'Pending')), ('pub', _(u'Published')), ('rej', _(u'Rejected')))

    name_en = models.CharField(max_length=255, verbose_name=_(u"English Name"))
    name_fa = models.CharField(blank=True, null=True, max_length=255, verbose_name=_(u"Persian Name"))

    website = models.URLField(unique=True, verbose_name=_(u"Website Url"))
    slug = models.SlugField(unique=True, verbose_name=_(u"Slug"))

    status = models.CharField(max_length=3, choices=STATUS, default='pen', verbose_name=_(u"Status"))

    average_p_rate = models.FloatField(default=0.0, verbose_name=_(u"Average People Rate"))
    average_e_rate = models.FloatField(default=0.0, verbose_name=_(u"Average Editor Rate"))
    ranking = models.FloatField(default=0.0, verbose_name=_(u"Ranking"))
    n_p_score = models.IntegerField(default=0, verbose_name=_(u"Net Promoter Score"))

    product_type = models.ForeignKey("Type", related_name="products", verbose_name=_("Type"),
                                     on_delete=models.CASCADE)
    categories = models.ManyToManyField("Category", related_name="products", verbose_name=_("Category"))

    hits = models.IntegerField(default=0, verbose_name=_(u"Hits"))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    version = models.ForeignKey("Version", related_name="+", blank=True, null=True, on_delete=models.SET_NULL)
    creator = models.ForeignKey(Profile, related_name="added_products", on_delete=models.SET(get_sentinel_user))

    class Meta:
        verbose_name = _(u'Product')
        verbose_name_plural = _(u'Products')

    def __str__(self):
        return self.name_en

    def last_approved_version(self):
        return self.version

    def save(self, *args, **kwargs):

        if self.slug is "" or self.slug is None:
            site = self.website
            site = site.split('?')[0]

            if site.startswith("http://"):
                site = site.replace("http://", "", 1)

            if site.startswith("https://"):
                site = site.replace("https://", "", 1)

            if site.startswith("www."):
                site = site.replace("www.", "", 1)

            if site.endswith("/"):
                site = site[:-1]

            extra = ""
            while Product.objects.filter(slug=site + extra).count() > 0:
                extra = str(int(random() * 1000))

            self.slug = site + extra

        if self.id is None and self.creator is not None:
            self.creator.user_point += 1
            self.creator.save()

        super(Product, self).save(*args, **kwargs)

    def hit(self):
        self.hits += 1
        self.save(update_fields=['hits'])

    def p_rate_count(self):
        return self.rates.filter(user_type=False).count()


def logo_dir(instance, filename):
    return '/'.join(['products/logo', "%s-%d" % (instance.version.id, filename)])


def banner_dir(instance, filename):
    return '/'.join(['products/banner', "%s-%d" % (instance.version.id, filename)])


class Version(models.Model):
    STATUS = (('pen', _(u'Pending')), ('pub', _(u'Published')), ('rej', _(u'Rejected')))

    status = models.CharField(max_length=3, choices=STATUS, default='pen', verbose_name=_(u"Status"))

    version_code = models.IntegerField()

    description_en = models.TextField(null=True, blank=True, verbose_name=_(u"English description"))
    description_fa = models.TextField(null=True, blank=True, verbose_name=_(u"Persian description"))

    email = models.EmailField(null=True, blank=True, verbose_name=_(u"Email"))
    android_app = models.URLField(null=True, blank=True, verbose_name=_(u"Android App"))
    ios_app = models.URLField(null=True, blank=True, verbose_name=_(u"iOS App"))
    linkedin = models.URLField(null=True, blank=True, verbose_name=_(u"Linkedin"))
    twitter = models.URLField(null=True, blank=True, verbose_name=_(u"Twitter"))
    instagram = models.URLField(null=True, blank=True, verbose_name=_(u"Instagram"))
    extra_url = models.URLField(null=True, blank=True, verbose_name=_(u"Extra Url"))

    # validation in forms: between 2100
    year = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name=_(u"Year Created"))

    city = models.CharField(null=True, blank=True, max_length=255, verbose_name=_(u"City"))
    country = models.CharField(null=True, blank=True, max_length=255, verbose_name=_(u"Country"))

    # validation in forms: x > 0
    employees = models.IntegerField(null=True, blank=True, verbose_name=_(u"Employees Count"))

    logo = models.ImageField(null=True, blank=True, upload_to='products/logo', verbose_name=_(u"Logo"))
    banner = models.ImageField(null=True, blank=True, upload_to='products/banner', verbose_name=_(u"Banner"))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    product = models.ForeignKey("Product", related_name="versions", verbose_name=_(u"Product"),
                                on_delete=models.CASCADE)
    editor = models.ForeignKey(Profile, related_name="versions", verbose_name=_(u"Editor"),
                               on_delete=models.SET(get_sentinel_user))
    responder = models.ForeignKey(Profile, related_name="responded_versions", verbose_name=_(u"Responder"),
                                  limit_choices_to={'user__is_superuser': True}, null=True, blank=True,
                                  on_delete=models.SET(get_sentinel_user))

    class Meta:
        verbose_name = _(u'Version')
        verbose_name_plural = _(u'Versions')

    def __str__(self):
        return "%s" % self.product

    def save(self, *args, **kwargs):

        approve_reject = False

        if self.id is None:
            version = 1
            try:
                version = self.product.versions.last().version_code + 1
            except:
                pass

            self.version_code = version

            if self.editor is not None:
                self.editor.user_point += 1
                self.editor.save(update_fields=['user_point'])

        else:
            origin = Version.objects.get(id=self.id)
            if origin.status != self.status:
                approve_reject = True

        super(Version, self).save(*args, **kwargs)

        if approve_reject:
            if self.status == "pub":
                self.approve()

    def approve(self):
        if self.can_respond():
            last_version = self.product.last_approved_version()

            if last_version and last_version.id < self.id:
                for field_name in Version._meta.get_fields():
                    if not field_name.name in ['created_at', 'updated_at', 'status', 'product', 'editor', 'responder',
                                               'version_code', 'id']:
                        field_value = getattr(self, field_name.name)
                        if not field_value or field_value is None or field_value == "" or field_value == []:
                            old_value = getattr(last_version, field_name.name)
                            setattr(self, field_name.name, old_value)
                self.save()

            self.product.version = self
            self.product.save(update_fields=['version'])

    def can_respond(self):
        return self.product.versions.filter(status='pen', id__lt=self.id).count() == 0

    def key_value_pairs(self):
        last_version = self.product.last_approved_version()
        output = {}
        for field_name in Version._meta.get_fields():
            if not field_name.name in ['created_at', 'updated_at', 'status', 'product', 'editor', 'responder',
                                       'version_code', 'id', 'description_en', 'description_fa', 'banner', 'logo']:
                field_value = getattr(self, field_name.name)
                if field_value:
                    output[field_name.name] = DataField(field_name.verbose_name, field_value)

        links = {'android_app': 'fa-google-play-badge', 'ios_app': 'fa-apple-store-badge',
                 'linkedin': 'fa-linkedin-square', 'twitter': 'fa-twitter-square', 'instagram': 'fa-instagram',
                 'extra_url': 'fa-globe'}

        for key in links:
            if key in output:
                output[key].make_link(links[key])

        return output


class Comment(models.Model):
    STATUS = (('pub', _(u'Published')), ('rej', _(u'Rejected')))

    status = models.CharField(max_length=3, choices=STATUS, default='pub', verbose_name=_(u"Status"))

    text = models.TextField(verbose_name=_("Text"))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    user = models.ForeignKey(Profile, related_name='comments', verbose_name=_("User"), on_delete=models.CASCADE)
    product = models.ForeignKey("Product", related_name="comments", verbose_name=_(u"Product"),
                                on_delete=models.CASCADE)

    class Meta:
        verbose_name = _(u'Comment')
        verbose_name_plural = _(u'Comments')

    def __str__(self):
        return "%s : %s" % (self.product, self.text)

    def save(self, *args, **kwargs):
        if self.id is None and self.user is not None:
            self.user.user_point += 1
            self.user.save(update_fields=['user_point'])

        super(Comment, self).save(*args, **kwargs)


class Rate(models.Model):
    # validation: 1 < x < 5
    rate = models.PositiveSmallIntegerField(default=1, verbose_name=_("Rate"))

    user = models.ForeignKey(Profile, related_name='rates', verbose_name=_("User"), on_delete=models.CASCADE)
    user_type = models.BooleanField(default=False, verbose_name=_("Type"))
    product = models.ForeignKey("Product", related_name="rates", verbose_name=_(u"Product"),
                                on_delete=models.CASCADE)

    class Meta:
        verbose_name = _(u'Rate')
        verbose_name_plural = _(u'Rates')

    def __str__(self):
        return "%s : %s" % (self.product, self.rate)

    def save(self, *args, **kwargs):
        if self.id is None and self.user is not None:
            self.user.user_point += 1
            self.user.save(update_fields=['user_point'])

        super(Rate, self).save(*args, **kwargs)

        average_rate = self.product.rates.filter(user_type=self.user_type).aggregate(Avg('rate'))['rate__avg']
        if self.user_type:
            self.product.average_e_rate = average_rate
        else:
            self.product.average_p_rate = average_rate

            p_rate_count = self.product.rates.filter(user_type=self.user_type).count()
            self.product.ranking = average_rate * (math.log10(p_rate_count) + 1)

        positive_rates = self.product.rates.filter(rate=5).count()
        negative_rates = self.product.rates.filter(rate__lte=3).count()
        if positive_rates + negative_rates > 0:
            self.product.n_p_score = (positive_rates - negative_rates) / (positive_rates + negative_rates) * 100
        else:
            self.product.n_p_score = 0

        self.product.save(update_fields=['average_p_rate', 'average_e_rate', 'n_p_score', 'ranking'])


class SocialLogin(models.Model):
    user = models.ForeignKey(User, verbose_name=_("User"), on_delete=models.CASCADE)
    social_unique_id = models.CharField(max_length=255, unique=True)