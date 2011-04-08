# -*- coding: utf-8 -*-

"""Admin classes."""

# TODO: Saving an object via TabularInline causes an error, as the user is not
#       given within the kwargs.

from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin import widgets
from django.core.urlresolvers import reverse
from django.db.models import Max, Q
from django.template.defaultfilters import truncatewords
from django.utils.translation import ugettext as _

from teagarden import models


class TabularInline(admin.TabularInline):

    def save_form(self, request, form, change):
        obj = form.save(commit=False)
        if not obj.id:
            obj.created_by = request.user
        obj.updated_by = request.user
        return obj

    def save_formset(request, form, formset, change=True):
        super(TabularInline, self).save_formset(request, form, formset, change)


### Forms ###

class ProjectForm(forms.ModelForm):
    
    name = forms.CharField(max_length=80, required=True,
        widget=forms.TextInput(attrs={"size": 40}))
    short_description = forms.CharField(max_length=40, required=False,
        widget=forms.TextInput(attrs={"size": 40}))
    description = forms.CharField(max_length=2000, required=False,
        widget=forms.Textarea(attrs={"cols": 80, "rows": 10}))
        
    class Meta:
        model = models.Project
    

class TableForm(forms.ModelForm):
    
    name = forms.CharField(max_length=30, required=True, 
        widget=forms.TextInput(attrs={"size": 30}))
    project = forms.ModelChoiceField(queryset=models.Project.objects.all())
    prefix = forms.CharField(max_length=3, required=False,
        widget=forms.TextInput(attrs={"size": 3}))
    type = forms.ModelChoiceField(models.TableType.objects.all())
    short_description = forms.CharField(max_length=40, required=False,
        widget=forms.TextInput(attrs={"size": 40}))
    description = forms.CharField(max_length=2000, required=False,
        widget=forms.Textarea(attrs={"cols": 80, "rows": 10}))
    

    class Meta:
        model = models.Table

    def clean(self):
        name = self.cleaned_data.get("name")
        project = self.cleaned_data.get("project")
        tables = models.Table.objects.filter(name=name, project=project)
        tables = tables.exclude(id=self.instance.id)
        if tables.count() > 0:
            raise forms.ValidationError(_(u"The tablename '%(table)s' is already in"
                                          " use for project '%(project)s'.")
                                        % {"table": name, "project": project})
        prefix = self.cleaned_data.get("prefix")
        tables = models.Table.objects.filter(project=project, prefix=prefix)
        tables = tables.exclude(id=self.instance.id)
        if tables.count() > 0:
            raise forms.ValidationError(_(u"The prefix '%(prefix)s' is already in use"
                                          " for project '%(project)s'.")
                                          % {"prefix": prefix, "project": project})
        return self.cleaned_data


### Inline Tables ###

class FieldKeyInline(TabularInline):

    fields = ("position","key")
    model = models.FieldKey
    verbose_name = _(u"Key")
    verbose_name_plural = _(u"Keys")


class FieldPropertyInline(TabularInline):

    fields = ("position", "property", "value")
    model = models.FieldProperty
    verbose_name = _(u"Property")
    verbose_name_plural = _(u"Properties")


class TableFieldInline(TabularInline):

    fields = ("position", "name", "type", "precision", "scaling", "primary",
              "foreign")
    model = models.Field
    verbose_name = _(u"Field")
    verbose_name_plural = _(u"Fields")


class TableGroupInline(TabularInline):

    fields = ("table",)
    model = models.TableGroup
    verbose_name = _(u"Table")
    verbose_name_plural = _(u"Tables")


class ModelAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        #obj.save(user=request.user.account)
        if getattr(obj, "created_by", None) is None:
            obj.created_by = request.user
        obj.updated_by = request.user
        obj.save()


### Widgets ###

class PrimaryKeyRawIdWidget(widgets.ForeignKeyRawIdWidget):

    def url_parameters(self):
        params = super(PrimaryKeyRawIdWidget, self).url_parameters()
        params["primary__exact"] = 1
        #print self.rel.get_related_field()
        #params["table__project__id__exact"] =
        return params
        
        
### Model Admin classes ###


class ProjectAdmin(ModelAdmin):

    fieldsets = [
        (None, {
            "fields": (
                       "name",
                       'short_description',
                       "description",),}),
        (_(u"Timestamp"), {
            "classes": ("collapse",),
            "fields": ["created", "created_by", "updated", "updated_by"]})
    ]
    form = ProjectForm
    list_display = ("id", "name", "short_description", "created", "created_by",
                    "updated", "updated_by")
    list_display_links = ("id", "name",)
    ordering = ["name"]
    readonly_fields = ["created", "created_by", "updated", "updated_by"]


class TableAdmin(ModelAdmin):

    actions = ["add_default_fields", "add_position_gaps"]
    date_hierarchy = "created"
    fieldsets = [
        (None, {
            "fields": ("name",
                       "project",
                       "prefix",
                       "type",)}),
        (_(u"Description"), {
            "fields": ("short_description", "description")}),
        (_(u"Database settings"), {
            "classes": ("collapse",),
            "fields": ["first_extension", "next_extension", "db_space",
                       "lock_mode", "storage_clause"]}),
        (_(u"Timestamp"), {
            "classes": ("collapse",),
            "fields": ["created", "created_by", "updated", "updated_by"]})

    ]
    form = TableForm
    inlines = [TableFieldInline]
    list_display = ("id", "name", "prefix", "type", "short_description",
                    "project", "count_fields", "created", "created_by",
                    "updated", "updated_by")
    list_display_links = ("id", "name",)
    list_filter = ["project", "type"]
    ordering = ["name"]
    readonly_fields = ["created", "created_by", "updated", "updated_by"]
    search_fields = ("name", "short_description", "description")

    def add_default_fields(self, request, queryset):
        """Attach the project's default fields to the selected tables."""
        num = 0L
        for table in queryset:
            fields_added = 0L
            default_fields = models.DefaultField.objects.filter(
                project=table.project).order_by("position")
            for df in default_fields:
                fields = models.Field.objects.filter(table=table, name=df.name)
                if fields.count() > 0:
                    continue
                fields_added += 1
                field = models.Field()
                field.name = df.name
                field.set_next_position(table)
                field.description = df.description
                field.short_description = df.short_description
                field.label = df.label
                field.type = df.type
                field.precision = df.precision
                field.scaling = df.scaling
                field.primary = df.primary
                field.foreign = df.foreign
                field.lookup = df.lookup
                field.nullable = df.nullable
                field.mask_length = df.mask_length
                field.default_value = df.default_value
                field.cascading_delete = df.cascading_delete
                field.table = table
                field.created_by = request.user
                field.updated_by = request.user
                field.save()
            if fields_added > 0:
                num += 1
        if num > 0:
            messages.success(request, _("Added default fields for %s tables."))
        else:
            messages.warning(request, _(u"No fields were added for the selected"
                                        u" tables."))
    add_default_fields.short_description = _(u"Add default fields to selected"
                                             " tables")

    def add_position_gaps(self, request, queryset):
        """Repositions all table fields."""
        for table in queryset:
            gap = settings.FIELD_POSITION_GAP
            for field in table.get_fields():
                field.position = gap
                field.save()
                gap += settings.FIELD_POSITION_GAP
        messages.success(request, _("Repositioned fields of selected tables."))
    add_position_gaps.short_description = _(u"Reposition fields of selected"
                                            u" tables")

    def copy_table(self, request, queryset):
        pass
    copy_table.short_description = _(u"Create a copy of the selected tables")

    def count_fields(self, obj):
        num = obj.count_fields()
        # admin/teagarden/field/?table__id__exact=1
        url = reverse("admin:teagarden_field_changelist")
        url += "?table__id__exact=%d" % obj.id
        return '<a href="%s">%s</a>' % (url, num)
    count_fields.allow_tags = True
    count_fields.short_description = _(u"Fields")

    def get_form(self, request, obj=None, **kwargs):
        form = super(TableAdmin, self).get_form(request, obj, **kwargs)
        if request.session.get("project", 0):
            form.base_fields["project"].initial = request.session["project"]
        return form
        
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if not isinstance(instance, models.Field):
                continue
            if not instance.position:
                instance.set_next_position()
                instance.set_timestamps(request.user)
                instance.save()

    def queryset(self, request):
        query = super(TableAdmin, self).queryset(request)
        if request.session.get("project", 0):
            project_id = request.session["project"]
            query = query.filter(project=int(project_id))
        return query


class TableTypeAdmin(ModelAdmin):

    fieldsets = [
        (None, {
            "fields": ("name",
                       "short_name",)}),
    ]
    list_display = ("id", "name", "short_name",)
    list_display_links = ("id", "name",)
    ordering = ["name"]


class FieldAdmin(ModelAdmin):

    inlines = [FieldPropertyInline, FieldKeyInline]
    fieldsets = [
        (None, {
            "fields": ("name",
                       "table",
                       "position")}),
        (_(u"Datatype"), {
            "fields": ("type",
                       "precision",
                       "scaling",
                       "default_value")}),
        (_(u"Constraints"), {
            "fields": ("primary",
                       "nullable",
                       "foreign")}),
        (_(u"Description"), {
            "fields": ("short_description",
                       "description")}),
        (_(u"Frontend"), {
            "fields": ("label",
                       "mask_length")}),
        (_(u"Database settings"), {
            "fields": ("cascading_delete",
                       "lookup")}),
        (_(u"Timestamp"), {
            "classes": ("collapse",),
            "fields": ["created", "created_by", "updated", "updated_by"]})
    ]
    list_display = ("id", "name", "type", "position", "primary",
                    "nullable", "foreign_table", "project", "get_table_name", "created",
                    "created_by", "updated", "updated_by")
    list_display_links = ("id", "name",)
    list_filter = ["table__project", "table", "primary"]
    ordering = ["table__project", "table", "position"]
    readonly_fields = ["created", "created_by", "updated", "updated_by"]
    raw_id_fields = ["foreign", "table"]
    search_fields = ["name"]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        db = kwargs.get("using")
        # TODO: Using the custom PrimaryKeyRawIdWidget causes the validation
        # to crash.
        #if db_field.name == "foreign":
            # Only display primary keys as possible foreign key connections
            #fields = models.Field.objects.filter(primary=True)
            #fields.order_by("table")
            #kwargs["queryset"] = fields
            #kwargs["to_field_name"] = "table"
            #kwargs["widget"] = PrimaryKeyRawIdWidget(db_field.rel, using=db)
            #return db_field.formfield(**kwargs)
            #return forms.ModelChoiceField(
                    #queryset=fields, required=not db_field.blank,
                    #initial=db_field.primary_key)
        return super(FieldAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs)

    #def formfield_for_foreignkey(self, db_field, request, **kwargs):
        #if db_field.name == "foreign":
            ## Only display primary keys as possible foreign key connections
            #fields = models.Field.objects.filter(primary=True)
            #fields.order_by("table")
            #kwargs["queryset"] = fields
            ##return db_field.formfield(**kwargs)
        #return super(FieldAdmin, self).formfield_for_foreignkey(
            #db_field, request, **kwargs)

    def foreign_table(self, obj):
        if obj.foreign:
            return obj.foreign.table
        else:
            return ""
    foreign_table.short_description = _(u"Foreign table")

    def full_name(self, obj):
        return obj.full_name()
    full_name.short_description = _(u"Full name")

    def get_table_name(self, obj):
        name = obj.table.name
        url = reverse("admin:teagarden_table_changelist")
        url += "%d" % obj.table.id
        return '<a href="%s">%s</a>' % (url, name)
    get_table_name.allow_tags = True
    get_table_name.short_description = _(u"Fields")
    get_table_name.admin_order_field = "table"
    
    def get_readonly_fields(self, request, obj=None):
        if isinstance(obj, models.Field):
            if obj.type.precision == False:
                self.readonly_fields.append("precision")
            if obj.type.scaling == False:
                self.readonly_fields.append("scaling")
        return self.readonly_fields

    def project(self, obj):
        return obj.table.project
    project.short_description = _(u"Project")

    def save_model(self, request, obj, form, change):
        # Automatically determine the fields new position
        if not obj.position:
            obj.set_next_position()
        super(FieldAdmin, self).save_model(request, obj, form, change)
        #obj.save()

    def queryset(self, request):
        query = super(FieldAdmin, self).queryset(request)
        if request.session.get("project", 0):
            project_id = request.session["project"]
            query = query.filter(table__project=int(project_id))
        return query


class FieldTypeAdmin(ModelAdmin):

    list_display = ("id", "name", "short_name", "precision", "scaling")
    list_display_links = ("id", "name",)
    ordering = ["id"]


class GroupAdmin(ModelAdmin):

    fieldsets = [
        (None, {
            "fields": ("name",
                       "project")}),
        (_(u"Timestamp"), {
            "classes": ("collapse",),
            "fields": ["created", "created_by", "updated", "updated_by"]})
    ]
    inlines = (TableGroupInline,)
    list_display = ("id", "name", "created", "created_by", "updated",
                    "updated_by")
    list_display_links = ("id", "name",)
    ordering = ["name"]
    readonly_fields = ["created", "created_by", "updated", "updated_by"]

    def get_form(self, request, obj=None, **kwargs):
        form = super(GroupAdmin, self).get_form(request, obj, **kwargs)
        if request.session.get("project", 0):
            form.base_fields["project"].initial = request.session["project"]
        return form

    def queryset(self, request):
        query = super(GroupAdmin, self).queryset(request)
        if request.session.get("project", 0):
            project_id = request.session["project"]
            query = query.filter(project=int(project_id))
        return query


class PropertyAdmin(ModelAdmin):

    fieldsets = [
        (None, {
            "fields": ("name",)}),
        (_(u"Timestamp"), {
            "classes": ("collapse",),
            "fields": ["created", "created_by", "updated", "updated_by"]})
    ]
    list_display = ("id", "name", "created", "created_by", "updated",
                    "updated_by")
    list_display_links = ("id", "name",)
    ordering = ["name"]
    readonly_fields = ["created", "created_by", "updated", "updated_by"]
    search_fields = ["name"]


class KeyAdmin(ModelAdmin):

    fieldsets = [
        (None, {
            "fields": ("unique",
                       "table",
                       "name")}),
        (_(u"Timestamp"), {
            "classes": ("collapse",),
            "fields": ["created", "created_by", "updated", "updated_by"]})
    ]
    list_display = ("id", "name", "unique", "table", "created", "created_by",
                    "updated", "updated_by")
    list_display_links = ("id", "name",)
    ordering = ["name"]
    readonly_fields = ["created", "created_by", "updated", "updated_by"]
    raw_id_fields = ["table"]

    def queryset(self, request):
        query = super(KeyAdmin, self).queryset(request)
        if request.session.get("project", 0):
            project_id = request.session["project"]
            query = query.filter(table__project=int(project_id))
        return query


class DefaultFieldAdmin(ModelAdmin):

    #inlines = [FieldPropertyInline, FieldKeyInline]
    fieldsets = [
        (None, {
            "fields": ("name",
                       "project",
                       "position")}),
        (_(u"Datatype"), {
            "fields": ("type",
                       "precision",
                       "scaling",
                       "default_value")}),
        (_(u"Constraints"), {
            "fields": ("primary",
                       "nullable",
                       "foreign")}),
        (_(u"Description"), {
            "fields": ("short_description",
                       "description")}),
        (_(u"Frontend"), {
            "fields": ("label",
                       "mask_length")}),
        (_(u"Database settings"), {
            "fields": ("cascading_delete",
                       "lookup")}),
        (_(u"Timestamp"), {
            "classes": ("collapse",),
            "fields": ["created", "created_by", "updated", "updated_by"]})
    ]
    list_display = ("id", "name", "type", "position", "primary",
                    "nullable", "foreign_table", "project", "created",
                    "created_by", "updated", "updated_by")
    list_display_links = ("id", "name",)
    list_filter = ["project"]
    ordering = ["position"]
    raw_id_fields = ["foreign"]
    readonly_fields = ["created", "created_by", "updated", "updated_by"]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        db = kwargs.get("using")
        #if db_field.name == "foreign":
            ## Only display primary keys as possible foreign key connections
            #fields = models.Field.objects.filter(primary=True)
            #fields.order_by("table")
            #kwargs["queryset"] = fields
            #kwargs["to_field_name"] = "table"
            #kwargs["widget"] = PrimaryKeyRawIdWidget(db_field.rel, using=db)
            #return db_field.formfield(**kwargs)
            #return forms.ModelChoiceField(
                    #queryset=fields, required=not db_field.blank,
                    #initial=db_field.primary_key)
        return super(DefaultFieldAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs)

    def foreign_table(self, obj):
        if obj.foreign:
            return obj.foreign.table
        else:
            return ""
    foreign_table.short_description = _(u"Foreign table")

    def get_form(self, request, obj=None, **kwargs):
        form = super(DefaultFieldAdmin, self).get_form(request, obj, **kwargs)
        if request.session.get("project", 0):
            form.base_fields["project"].initial = request.session["project"]
        return form

    def project(self, obj):
        return obj.project
    project.short_description = _(u"Project")

    def save_model(self, request, obj, form, change):
        if not obj.position:
            fields = models.DefaultField.objects.filter(project=obj.project)
            # Automatically determine the fields new position
            max = fields.aggregate(Max("position"))["position__max"] or 0
            obj.position = max + settings.FIELD_POSITION_GAP
        super(DefaultFieldAdmin, self).save_model(request, obj, form, change)
        #obj.save()

    def queryset(self, request):
        query = super(DefaultFieldAdmin, self).queryset(request)
        if request.session.get("project", 0):
            project_id = request.session["project"]
            query = query.filter(project=int(project_id))
        return query
        
        
class CommentAdmin(ModelAdmin):
    
    list_display = ("content_type", "object_id", "content_object", "is_draft",
                    "text", "created", "created_by", "updated", "updated_by")
    list_display_links = ("content_type",)


class TableGroupAdmin(ModelAdmin):

    fieldsets = [
        (None, {
            "fields": ("group",
                       "table")}),
        (_(u"Timestamp"), {
            "classes": ("collapse",),
            "fields": ["created", "created_by", "updated", "updated_by"]})
    ]
    list_display = ("id", "group", "table", "created", "created_by", "updated",
                    "updated_by")
    list_display_links = ("id",)
    readonly_fields = ["created", "created_by", "updated", "updated_by"]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        project_id = request.session.get("project", 0)
        if db_field.name == "table" and project_id:
            query = models.Table.objects.filter(
                project__id=project_id).order_by("name")
            #query = query.values_list('id')
            kwargs["queryset"] = query
            kwargs["to_field_name"] = "name"
            #return forms.ModelChoiceField(
                #queryset=query, required=not db_field.blank,
                #initial=db_field.primary_key)
            return db_field.formfield(**kwargs)
        elif db_field.name == "group" and project_id:
            query = models.Group.objects.filter(project__id=project_id)
            kwargs["queryset"] = query
            kwargs["to_field_name"] = "name"
            return db_field.formfield(**kwargs)
        return super(TableGroupAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs)

    def queryset(self, request):
        query = super(TableGroupAdmin, self).queryset(request)
        if request.session.get("project", 0):
            project_id = request.session["project"]
            query = query.filter(table__project=int(project_id))
        return query


admin.site.register(models.Comment, CommentAdmin)
admin.site.register(models.DefaultField, DefaultFieldAdmin)
admin.site.register(models.Field, FieldAdmin)
#admin.site.register(models.FieldComment, FieldCommentAdmin)
admin.site.register(models.FieldType, FieldTypeAdmin)
admin.site.register(models.Group, GroupAdmin)
admin.site.register(models.Key, KeyAdmin)
admin.site.register(models.Project, ProjectAdmin)
admin.site.register(models.Property, PropertyAdmin)
admin.site.register(models.Table, TableAdmin)
#admin.site.register(models.TableComment, TableCommentAdmin)
admin.site.register(models.TableGroup, TableGroupAdmin)
admin.site.register(models.TableType, TableTypeAdmin)
