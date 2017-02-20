from django import forms
from django.contrib import admin
from iran_list.products.models import Type, Category, Product, Profile, Version, Comment, Rate
from django.utils.translation import ugettext_lazy as _


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = []


class ProductAdmin(admin.ModelAdmin):
    form = ProductForm

    list_display = ['name_en', 'status', 'created_at']
    list_filter = ('product_type', 'status', 'categories')
    filter_horizontal = ('categories',)
    readonly_fields = ['creator', 'created_at', 'updated_at', 'slug']

    class Meta:
        exclude = []


class VersionForm(forms.ModelForm):
    class Meta:
        model = Version
        exclude = ["responder"]

    def clean(self):
        cleaned_data = super(VersionForm, self).clean()

        if not self.instance.can_respond():
            raise forms.ValidationError(_(u"Can't respond to this version. Check earlier versions."))


class VersionAdmin(admin.ModelAdmin):
    form = VersionForm

    list_display = ['__str__', 'version_code', 'status']
    list_filter = ('product', 'status')
    readonly_fields = ['version_code', 'product', 'editor', 'created_at', 'updated_at']

    class Meta:
        exclude = []


admin.site.register(Type)
admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
admin.site.register(Version, VersionAdmin)
admin.site.register(Profile)
admin.site.register(Comment)
admin.site.register(Rate)
