from django.contrib import admin
from booking.admin import disable_fields
from .models import Page, PageComponent, Elements, Languages, Content
from rest_framework_simplejwt.token_blacklist import models as jwt_models

class PageAdmin(admin.ModelAdmin):
    list_display = ['title', 'url', 'created_by', 'updated_by']
    search_fields = ['title']
    list_per_page = 10

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ['created_by', 'updated_by']:
            kwargs['disabled'] = True
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return disable_fields(form,obj)

    def save_model(self, request, obj, form, change):
        # Set created_by field for new objects
        if not change:
            obj.created_by = request.user
        # Set updated_by field for new and existing objects
        obj.updated_by = request.user
        # Call the super method to save the object
        super().save_model(request, obj, form, change)


class ContentAdmin(admin.ModelAdmin):
    list_display = ['name', 'component', 'element', 'page','content_order']
    search_fields = ['name','content_value']
    list_per_page = 10

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ['created_by', 'updated_by']:
            kwargs['disabled'] = True
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def page(self, obj):
        return obj.page_id  # Getting page_id

    page.short_description = 'Page'  # Customize the column name in admin panel

    def element(self, obj):
        return obj.element_id

    element.short_description = 'Element'

    def component(self, obj):
        return obj.component_id

    component.short_description = 'Component'

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return disable_fields(form,obj)

    def save_model(self, request, obj, form, change):
        # Set created_by field for new objects
        if not change:
            obj.created_by = request.user
        # Set updated_by field for new and existing objects
        obj.updated_by = request.user
        # Call the super method to save the object
        super().save_model(request, obj, form, change)

    # def has_delete_permission(self, request, obj=None):
    #     return False


class ComponentAdmin(admin.ModelAdmin):
    list_display = ['name', 'page', 'created_by', 'updated_by']
    search_fields = ['name']
    list_per_page = 10

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ['created_by', 'updated_by']:
            kwargs['disabled'] = True
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def page(self, obj):
        return obj.page_id

    page.short_description = 'Page'

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return disable_fields(form,obj)

    def save_model(self, request, obj, form, change):
        # Set created_by field for new objects
        if not change:
            obj.created_by = request.user
        # Set updated_by field for new and existing objects
        obj.updated_by = request.user
        # Call the super method to save the object
        super().save_model(request, obj, form, change)


class ElementAdmin(admin.ModelAdmin):
    list_display = ['name', 'component', 'page', 'created_by', 'updated_by']
    search_fields = ['name']
    list_per_page = 10

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ['created_by', 'updated_by']:
            kwargs['disabled'] = True
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def page(self, obj):
        return obj.page_id

    page.short_description = 'Page'

    def component(self, obj):
        return obj.component_id

    component.short_description = 'Component'

    def get_form(self, request, obj=None, **kwargs):
        
        form = super().get_form(request, obj, **kwargs)
        if form:
            return disable_fields(form,obj)
        return form

    def save_model(self, request, obj, form, change):
        # Set created_by field for new objects
        if not change:
            obj.created_by = request.user
        # Set updated_by field for new and existing objects
        obj.updated_by = request.user
        # Call the super method to save the object
        super().save_model(request, obj, form, change)


class LanguageAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'updated_by']
    search_fields = ['name']
    list_per_page = 10

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ['created_by', 'updated_by']:
            kwargs['disabled'] = True
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if form:
           return disable_fields(form,obj)
        return form

    def save_model(self, request, obj, form, change):
        # Set created_by field for new objects
        if not change:
            obj.created_by = request.user
        # Set updated_by field for new and existing objects
        obj.updated_by = request.user
        # Call the super method to save the object
        super().save_model(request, obj, form, change)


admin.site.unregister(jwt_models.OutstandingToken)
admin.site.unregister(jwt_models.BlacklistedToken)
admin.site.register(Page, PageAdmin)
admin.site.register(Languages,LanguageAdmin)
admin.site.register(PageComponent, ComponentAdmin)
admin.site.register(Elements, ElementAdmin)
admin.site.register(Content, ContentAdmin)