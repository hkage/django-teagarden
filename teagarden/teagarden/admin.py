# -*- coding: utf-8 -*-

"""Admin model definitions"""

from django.contrib import admin
from django.utils.translation import ugettext as _

import reversion

from teagarden import models


class FieldTypeAdmin(reversion.VersionAdmin):

    list_display = ('name', 'short_name', 'created', 'created_by', 'modified',
                    'modified_by')


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

    list_display = ('name', 'prefix', 'prefix', 'type', 'project',
                    'created', 'created_by', 'modified', 'modified_by')
    list_filter = ('project', 'type')


class TableTypeAdmin(reversion.VersionAdmin):

    list_display = ()


admin.site.register(models.FieldType, FieldTypeAdmin)
admin.site.register(models.Project, ProjectAdmin)
admin.site.register(models.Table, TableAdmin)
admin.site.register(models.TableType, TableTypeAdmin)
