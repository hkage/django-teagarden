# -*- coding: utf-8 -*-

"""Admin model definitions"""

from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

import reversion

from teagarden import models


class TableFieldInline(admin.TabularInline):

    extra = 0
    fields = ('position', 'name', 'type', 'precision', 'scaling', 'primary',
              'foreign')
    model = models.Field
    verbose_name = _(u'Field')
    verbose_name_plural = _(u'Fields')


class TableGroupInline(admin.TabularInline):

    #fields = ('table',)
    extra = 0
    model = models.Table.group.through
    verbose_name = _(u'Table')
    verbose_name_plural = _(u'Tables')


class TableForm(forms.ModelForm):

    class Meta:
        model = models.Table

    def clean(self):
        project = self.cleaned_data.get('project')
        prefix = self.cleaned_data.get('prefix')
        if prefix:
            query = models.Table.objects.filter(project=project, prefix=prefix)
            query = query.exclude(id=self.instance.id)
            if query.count() > 0:
                raise forms.ValidationError(
                    _(u'The prefix \'%(prefix)s\' is already in use for'
                      u' project \'%(project)s\'.')
                    % {'prefix': prefix, 'project': project})
        return self.cleaned_data


class FieldAdmin(reversion.VersionAdmin):

    fieldsets = [
        (None, {
            'fields': ('name',
                       'table',
                       'position')}),
        (_(u'Datatype'), {
            'fields': ('type',
                       'precision',
                       'scaling',
                       'default_value')}),
        (_(u'Constraints'), {
            'fields': ('primary',
                       'nullable',
                       'foreign')}),
        (_(u'Description'), {
            'fields': ('short_description',
                       'description')}),
        (_(u'Frontend'), {
            'fields': ('label',
                       'mask_length')}),
        (_(u'Database settings'), {
            'fields': ('cascading_delete',
                       'lookup')}),
    ]
    list_display = ('name', 'type', 'position', 'primary',
                    'nullable', 'foreign_table', 'project', 'get_table_name',
                    'created', 'created_by', 'modified', 'modified_by')
    list_filter = ['table__project', 'table', 'primary']
    search_fields = ('name',)

    def foreign_table(self, obj):
        if obj.foreign:
            return obj.foreign.table
        else:
            return ''
    foreign_table.short_description = _(u'Foreign table')

    def get_table_name(self, obj):
        name = obj.table.name
        url = reverse('admin:teagarden_table_changelist')
        url += '%d' % obj.table.id
        return '<a href=\'%s\'>%s</a>' % (url, name)
    get_table_name.allow_tags = True
    get_table_name.short_description = _(u'Fields')
    get_table_name.admin_order_field = 'table'

    def project(self, obj):
        return obj.table.project
    project.short_description = _(u'Project')

    def save_model(self, request, obj, form, change):
        # Automatically determine the fields new position
        if not obj.position:
            obj.set_next_position()
        super(FieldAdmin, self).save_model(request, obj, form, change)
        #obj.save()


class FieldTypeAdmin(reversion.VersionAdmin):

    list_display = ('name', 'short_name', 'created', 'created_by', 'modified',
                    'modified_by')


class GroupAdmin(reversion.VersionAdmin):

    inlines = (TableGroupInline,)
    list_display = ('project', 'name', 'created', 'created_by', 'modified',
                    'modified_by')
    list_filter = ('project',)


class ProjectAdmin(reversion.VersionAdmin):

    fieldsets = [
        (None, {
            'fields': (
                'name',
                'short_description',
                'description',),}),
        ]
    list_display = ('name', 'created', 'created_by', 'modified', 'modified_by')


class TableAdmin(reversion.VersionAdmin):

    actions = ('add_position_gaps',)
    fieldsets = [
        (None, {
            'fields': ('name',
                       'project',
                       'group',
                       'prefix',
                       'type',)}),
        (_(u'Description'), {
            'fields': ('short_description', 'description')}),
    ]
    form = TableForm
    inlines = [TableFieldInline]
    list_display = ('name', 'prefix', 'type', 'project',
                    'created', 'created_by', 'modified', 'modified_by')
    list_filter = ('project', 'type', 'group')
    # raw_id_fields = ('group',)
    search_fields = ('name', 'short_description', 'description')

    def add_position_gaps(self, request, queryset):
        """Repositions all table fields."""
        for table in queryset:
            gap = settings.FIELD_POSITION_GAP
            for field in table.fields.all():
                field.position = gap
                field.save()
                gap += settings.FIELD_POSITION_GAP
        messages.success(request,
                         _(u'Repositioned fields of selected tables.'))
    add_position_gaps.short_description = _(u'Reposition fields of selected'
                                            u' tables')


class TableTypeAdmin(reversion.VersionAdmin):

    list_display = ()


admin.site.register(models.Field, FieldAdmin)
admin.site.register(models.FieldType, FieldTypeAdmin)
admin.site.register(models.Group, GroupAdmin)
admin.site.register(models.Project, ProjectAdmin)
admin.site.register(models.Table, TableAdmin)
admin.site.register(models.TableType, TableTypeAdmin)
