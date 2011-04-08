# -*- coding: utf-8 -*-

import datetime

from django.conf import settings
from django.contrib.auth.models import User, UserManager
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.cache import cache
from django.db import models
from django.utils.translation import ugettext as _

# Monkey-patch DEFAULT_NAMES for Meta options. Otherwise
# db_column_prefix would raise an error.
from django.db.models import options
options.DEFAULT_NAMES += ("db_column_prefix",)

import filter


LOOKUP_CHOICES = (
    (u"L", _(u"Lookup")),
    (u"D", _(u"Detail"))
)

COMMENT_TABLES = (
    ("feld", _(u"Field")),
    ("tabelle", _(u"Table"))
)


def save_user_trigger(sender, instance, **kwds):
    if cache.has_key("user:%d" % instance.id):
        cache.delete("user:%d" % instance.id)
    if cache.has_key("user_popup:%d" % instance.id):
        cache.delete("user_popup:%d" % instance.id)


class ColumnPrefixModelMeta(models.base.ModelBase):

    def __new__(cls, name, bases, attrs):
        new_cls = super(ColumnPrefixModelMeta, cls).__new__(
            cls, name, bases, attrs)
        prefix = getattr(new_cls._meta, "db_column_prefix", None)
        # db_column_prefix on abstract base classes will be ignored.
        if not new_cls._meta.abstract and prefix is not None:
            # Shamelessly stolen from ModelBase.__new__:
            new_fields = new_cls._meta.local_fields + \
                         new_cls._meta.local_many_to_many + \
                         new_cls._meta.virtual_fields
            for field in new_fields:
                if isinstance(field, generic.GenericForeignKey):
                    continue
                if field.db_column is None:
                    field.db_column = field.get_attname()
                if not field.db_column.startswith(prefix):
                    field.db_column = "%s%s" % (prefix, field.db_column)
                # This sets field.column which is needed for build SQL
                # statements
                field.set_attributes_from_name(field.name)
        return new_cls


class BaseModel(models.Model):
    """Base class for all model classes."""

    __metaclass__ = ColumnPrefixModelMeta

    class Meta:
        abstract = True

    @classmethod
    def get_by_id(cls, id):
        """Returns a query object by it's primary key.

        :param id: Id of the query object
        :returns: Instance of cls or None
        """
        try:
            id = int(id)
        except (ValueError, TypeError):
            return None
        query = cls.objects.filter(id=id)
        if query.count() == 0:
            raise cls.DoesNotExist
        elif query.count() == 1:
            return query[0]
        return query
        
    def set_timestamps(self, user):
        if not self.id:
            self.created = datetime.datetime.now()
            self.created_by = user
        self.updated = datetime.datetime.now()
        self.updated_by = user

#    def save(self, *args, **kwds):
#        """Derived save method to automatically save timestamp values."""
#        now = datetime.datetime.now()
#        user = kwds.pop('user')
#        if not self.id:
#            self.created = now
#            self.created_by = user
#        self.updated = now
#        self.updated_by = user
#        super(BaseModel, self).save(*args, **kwds)


class TimestampModel(BaseModel):
    """Base class for all models that need timestamp fields.

    This base class provides default fields that should be used by all
    models in this module.
    """

    created_by = models.ForeignKey(User, blank=True, null=True, editable=False,
                                  db_column="crid",
                                  related_name="%(class)s_creators",
                                  verbose_name=_(u"Created by"))
    updated_by = models.ForeignKey(User, blank=True, null=True, editable=False,
                                   db_column="updid",
                                   related_name="%(class)s_modifiers",
                                   verbose_name=_(u"Modified by"))
    created = models.DateTimeField(auto_now_add=True, db_column="crdate")
    updated = models.DateTimeField(auto_now=True, db_column="upddate")

    class Meta:
        abstract = True
        
        
class CommentProvider(object):
    """Helper class for all tables, that provide a comment interface."""
    
    def count_comments(self):
        query = self.get_comments().filter(is_draft=False)
        return query.count()
        
    def count_drafts(self):
        query = self.get_comments().filter(is_draft=True)
        return query.count()
        
    def get_comments(self):
        ct = ContentType.objects.get_for_model(self)
        return Comment.objects.filter(content_type__pk=ct.id,
                                      object_id=self.id)
                                      
    def get_comments_by_date(self):
        query = self.get_comments().filter(is_draft=False)
        return query.order_by("created")
        
        
class StarredItemProvider(object):
    
    def is_starred(self, user):
        ct = ContentType.objects.get_for_model(self)
        query = StarredItem.objects.filter(content_type__pk=ct.id,
            object_id=self.id, user=user)
        return query.count() == 1
        
    def add_star(self, user):
        star = StarredItem(content_object=self)
        star.user = user
        star.save()
        
    def remove_star(self, user):
        ct = ContentType.objects.get_for_model(self)
        query = StarredItem.objects.filter(content_type__pk=ct.id,
            object_id=self.id, user=user)
        query.delete()
        

class Account(User):
    """Extends the django default user."""

    current_user_account = None
    starred_fields = []
    starred_tables = []

    class Meta:
        proxy = True


    @classmethod
    def get_account_for_user(cls, user):
        #assert user.email
        #query = Account.objects.filter(email=user.email)
        #account = tuple(query)[0] or None
        #if account is not None:
        #    return account
        query = Account.objects.filter(username=user.username)
        account = tuple(query)[0] or None
        if account is not None:
            return account

    @property
    def nickname(self):
        if self.first_name and self.last_name:
            return u"%s %s" % (self.first_name, self.last_name)
        else:
            return self.username

    @property
    def num_comments(self):
        num = 0L
        comments = TableComment.objects.filter(created_by=self.id)
        comments = comments.filter(is_draft=False)
        num += comments.count()
        comments = FieldComment.objects.filter(created_by=self.id)
        comments = comments.filter(is_draft=False)
        num += comments.count()
        return num

    @property
    def num_tables(self):
        tables = Table.objects.filter(created_by=self.id)
        return tables.count()


models.signals.post_save.connect(save_user_trigger, sender=User)


class Project(TimestampModel):

    id = models.AutoField(primary_key=True, db_column="id",
                          verbose_name=_(u"Id"))
    name = models.CharField(max_length=80, db_column="name", null=False,
                            blank=False, verbose_name=_(u"Name"),
                            unique=True)
    short_description = models.CharField(max_length=40,
                                         db_column="zuname", null=True,
                                         blank=True,
                                         verbose_name=_(u"Short description"))
    description = models.CharField(max_length=256, db_column="txt",
                                   null=True, blank=True,
                                   verbose_name=_(u"Description"))

    class Meta:
        db_table = u"projekt"
        db_column_prefix = u"pr_"
        ordering = ("name",)
        verbose_name = _(u"Project")
        verbose_name_plural = _(u"Projects")

    def __unicode__(self):
        return self.name

    def count_tables(self):
        return Table.objects.filter(project=self.id).count()


class Table(TimestampModel, CommentProvider, StarredItemProvider):

    id = models.AutoField(primary_key=True, db_column="id",
                          verbose_name=_(u"Id"))
    name = models.CharField(max_length=30, db_column="name", null=False,
                            blank=False, verbose_name=_(u"Name"))
    prefix = models.CharField(max_length=3, db_column="prae", null=True,
                              blank=True, verbose_name=_(u"Prefix"))
    type = models.ForeignKey("TableType", db_column="ttid", null=False,
                             blank=False, verbose_name=_(u"Type"))
    short_description = models.CharField(max_length=40,
                                         db_column="zuname", null=True,
                                         blank=True,
                                         verbose_name=_(u"Short description"))
    description = models.CharField(max_length=2000, db_column="txt",
                                   null=True, blank=True,
                                   verbose_name=_(u"Description"))
    project = models.ForeignKey("Project", db_column="prid", null=False,
                                blank=False, verbose_name=_(u"Project"))
    first_extension = models.IntegerField(db_column="fext", null=True,
                                          blank=True,
                                          verbose_name=_(u"First extension"))
    next_extension = models.IntegerField(db_column="next", null=True,
                                         blank=True,
                                         verbose_name=_(u"Next extension"))
    db_space = models.IntegerField(db_column="dbspc", null=True,
                                   blank=True,
                                   verbose_name=_(u"Database space"))
    lock_mode = models.CharField(max_length=1, db_column="lckmode",
                                 null=True, blank=True,
                                 verbose_name=_(u"Lockmode"))
    storage_clause = models.CharField(max_length=4000, db_column="stclause",
                                      null=True, blank=True,
                                      verbose_name=_(u"Storage clause"))

    #project.project_filter = True

    _is_starred = None

    class Meta:
        db_table = u"tabelle"
        db_column_prefix = u"ta_"
        ordering = ("name",)
        unique_together = ("project", "name")
        verbose_name = _(u"Table")
        verbose_name_plural = _(u"Tables")

    def __unicode__(self):
        return self.name

    @property
    def foreign_keys(self):
        fields = Field.objects.filter(table=self.id)
        fields = fields.filter(foreign__isnull=False)
        fields = fields.order_by("position")
        return fields

    #@property
    #def is_starred(self):
        #"""Whether the current user has this booking starred."""
        #if self._is_starred is not None:
        #    return self._is_starred
        #account = Account.current_user_account
        #self._is_starred = account is not None and self.id in account.starred_tables
        #return self._is_starred
        
    @models.permalink
    def get_absolute_url(self):
        return ('teagarden.views.table', [str(self.id)])

    def copy(self, name=None, with_fields=False):
        """Copy a table, optional with fields.

        :param name: Name of the new table.
        :param with_fields: Copy the table's fields.
        :returns: :class:`Table` instance.
        """
        new = Table()
        if name is not None:
            new.name = name
        else:
            new.name = _(u"Copy of '%s'") % self.name
        new.prefix = None
        new.type = self.type
        new.short_description = None
        new.description = None
        new.project = self.project
        if not with_fields:
            return new
        for field in self.get_fields():
            pass
        return new

    def count_fields(self):
        return Field.objects.filter(table=self.id).count()

    def get_fields(self, ordered=True):
        query = Field.objects.filter(table=self.id)
        if ordered:
            query = query.order_by("position")
        return query


class TableType(BaseModel):

    id = models.AutoField(primary_key=True, db_column="id",
                          verbose_name=_(u"Id"))
    name = models.CharField(max_length=15, db_column="name", null=False,
                            blank=False, unique=True,
                            verbose_name=_(u"Name"))
    short_name = models.CharField(max_length=3, db_column="kurz",
                                  null=False, blank=False, unique=True,
                                  verbose_name=_(u"Short name"))

    class Meta:
        db_table = u"tabellentyp"
        db_column_prefix = u"tt_"
        ordering = ("name",)
        verbose_name = _(u"Tabletype")
        verbose_name_plural = _(u"Tabletypes")

    def __unicode__(self):
        return self.name


class Field(TimestampModel, CommentProvider):

    _is_starred = None
    _n_comments = None
    _n_drafts = None

    id = models.AutoField(primary_key=True, db_column="id",
                          verbose_name=_(u"Id"))
    name = models.CharField(max_length=60, db_column="name", null=False,
                            blank=False, verbose_name=_(u"Name"))
    position = models.IntegerField(db_column="pos", null=True, blank=True,
                                   verbose_name=_(u"Position"))
    short_description = models.CharField(max_length=60, db_column="zuname",
                                         null=False, blank=False,
                                         verbose_name=_(u"Short description"))
    description = models.CharField(max_length=2000, db_column="txt",
                                   null=True, blank=True,
                                   verbose_name=_(u"Description"))
    label = models.CharField(max_length=60, db_column="label", null=False,
                             blank=False, verbose_name=_(u"Label"))
    type = models.ForeignKey("FieldType", db_column="ftid", null=False,
                             blank=False, verbose_name=_(u"Type"))
    precision = models.CharField(max_length=12, db_column="zus1",
                                 null=True, blank=True,
                                 verbose_name=_(u"Precision"))
    scaling = models.CharField(max_length=12, db_column="zus2",
                               null=True, blank=True,
                               verbose_name=_(u"Scaling"))
    primary = models.BooleanField(db_column="prim", null=False, blank=False,
                                  verbose_name=_(u"Primary"))
    foreign = models.ForeignKey("self", db_column="fremd_feid",
                                null=True, blank=True,
                                on_delete=models.SET_NULL,
                                verbose_name=_(u"Foreign key"))
    lookup = models.CharField(max_length=2, db_column="look",
                              null=True, blank=True, choices=LOOKUP_CHOICES,
                              verbose_name=_(u"Lookup?"))
    nullable = models.BooleanField(db_column="null", null=False,
                                   blank=False,
                                   verbose_name=_(u"Nullable"))
    mask_length = models.IntegerField(db_column="mlang", null=False,
                                      blank=False, default=0,
                                      verbose_name=_(u"Mask length"))
    default_value = models.CharField(max_length=32, db_column="default",
                                     null=True, blank=True,
                                     verbose_name=_(u"Default value"))
    cascading_delete = models.BooleanField(db_column="loesch",
                                           default=False,
                                           verbose_name=_(u"Cascading delete"))
    table = models.ForeignKey("Table", db_column="taid", null=False,
                              blank=False, related_name="fields",
                              verbose_name=_(u"Table"))

    class Meta:
        db_table = u"feld"
        db_column_prefix = u"fe_"
        ordering = ("position",)
        unique_together = ("name", "table")
        verbose_name = _(u"Field")
        verbose_name_plural = _(u"Fields")

    def __unicode__(self):
        return self.name

    #def _get_num_comments(self, drafts_only=False):
        #return FieldComment.objects.filter(
            #field=self, is_draft=drafts_only).count()

    @property
    def is_starred(self):
        """Whether the current user has this field starred."""
        if self._is_starred is not None:
            return self._is_starred
        account = Account.current_user_account
        self._is_starred = account is not None and self.id in account.starred_fields
        return self._is_starred

    #@property
    #def num_comments(self):
    #    if self._n_comments is None:
    #        self._n_comments = self._get_num_comments()
    #    return self._n_comments

    #@property
    #def num_drafts(self):
    #    if self._n_drafts is None:
    #        self._n_drafts = self._get_num_comments(drafts_only=True)
    #    return self._n_drafts

    def full_name(self):
        """Return a qualified name by table and prefix, if given.
        
        :returns: Name as string
        """
        if self.table.prefix:
            return "%s_%s" % (self.table.prefix, self.name)
        else:
            return self.name

    def full_type(self):
        retval = "%s" % self.type
        if self.precision and self.scaling:
            retval += " (%s, %s)" % (self.precision, self.scaling)
        elif self.precision and not self.scaling:
            retval += " (%s)" % self.precision
        return retval

    #def get_comments_by_date(self):
        #return FieldComment.objects.filter(field=self,
                                           #is_draft=False).order_by("created")

    def set_next_position(self, table=None):
        """Set the next available position for this field.
        
        :param table: A :class:`Table` instance
        """
        if not table:
            table = self.table
        fields = Field.objects.filter(table=table)
        max = fields.aggregate(models.Max("position"))["position__max"] or 0
        self.position = max + settings.FIELD_POSITION_GAP


class FieldProperty(TimestampModel):

    id = models.AutoField(primary_key=True, db_column="id",
                          verbose_name=_(u"Id"))
    position = models.IntegerField(db_column="pos", null=False,
                                   verbose_name=_(u"Position"))
    property = models.ForeignKey("Property", db_column="etid", null=False,
                                 blank=False,
                                 verbose_name=_(u"Property"))
    field = models.ForeignKey("Field", db_column="feid", null=False,
                              blank=False,
                              verbose_name=_(u"Field"))
    value = models.CharField(max_length=256, db_column="wert",
                             verbose_name=_(u"Value"))

    class Meta:
        db_table = u"feldeigenschaft"
        db_column_prefix = u"fei_"
        unique_together = ("property", "field")
        verbose_name = _(u"Field property")
        verbose_name_plural = _(u"Field properties")


class FieldType(BaseModel):

    id = models.AutoField(primary_key=True, db_column="id",
                          verbose_name=_(u"Id"))
    name = models.CharField(max_length=15, db_column="name", null=False,
                            blank=False, unique=True,
                            verbose_name=_(u"Name"))
    short_name = models.CharField(max_length=3, db_column="kurz",
                                  null=False, blank=False, unique=True,
                                  verbose_name=_(u"Short name"))
    precision = models.BooleanField(db_column="zus1", null=False,
                                 blank=False, default=False,
                                 verbose_name=_(u"Precision"))
    scaling = models.BooleanField(db_column="zus2", null=False,
                               blank=False, default=False,
                               verbose_name=_(u"Scaling"))

    class Meta:
        db_table = u"feldtyp"
        db_column_prefix = u"ft_"
        ordering = ("name",)
        verbose_name = _(u"Fieldtype")
        verbose_name_plural = _(u"Fieldtypes")

    def __unicode__(self):
        return self.name


class Group(TimestampModel):

    id = models.AutoField(primary_key=True, db_column="id",
                          verbose_name=_(u"Id"))
    name = models.CharField(max_length=60, db_column="name", blank=False,
                            null=False, verbose_name=_(u"Name"))
    project = models.ForeignKey("Project", db_column="prid", blank=False,
                                null=False, verbose_name=_("Project"))

    class Meta:
        db_table = u"gruppe"
        db_column_prefix = u"gr_"
        ordering = ("name",)
        unique_together = ("project", "name")
        verbose_name = _(u"Group")
        verbose_name_plural = _(u"Groups")

    def __unicode__(self):
        return self.name


class Property(TimestampModel):

    id = models.AutoField(primary_key=True, db_column="id",
                          verbose_name=_(u"Id"))
    name = models.CharField(max_length=60, db_column="bez", blank=False,
                            null=False, verbose_name=_(u"Name"))

    class Meta:
        db_table = u"eigenschafttyp"
        db_column_prefix = u"et_"
        ordering = ("name",)
        verbose_name = _(u"Property")
        verbose_name_plural = _(u"Properties")

    def __unicode__(self):
        return self.name


class TableGroup(TimestampModel):

    id = models.AutoField(primary_key=True, db_column="id",
                          verbose_name=_(u"Id"))
    table = models.ForeignKey("Table", db_column="taid", blank=False,
                              null=False, verbose_name=_(u"Table"))
    group = models.ForeignKey("Group", db_column="grid", blank=False,
                              null=False, verbose_name=_(u"Group"))

    class Meta:
        db_table = u"tabgruppe"
        db_column_prefix = u"tg_"
        unique_together = ("table", "group")
        verbose_name = _(u"Table group")
        verbose_name_plural = _(u"Table groups")


class Key(TimestampModel):

    id = models.AutoField(primary_key=True, db_column="id",
                          verbose_name=_(u"Id"))
    unique = models.BooleanField(db_column="uni", default=False,
                                 verbose_name=_(u"Unique"))
    table = models.ForeignKey("Table", db_column="taid",
                              verbose_name=_(u"Table"))
    name = models.CharField(max_length=255, db_column="name",
                            verbose_name=_(u"Name"))

    class Meta:
        db_table = u"schluess"
        db_column_prefix = u"sc_"
        ordering = ("name",)
        verbose_name = _(u"Key")
        verbose_name_plural = _(u"Keys")

    def __unicode__(self):
        return self.name


class FieldKey(TimestampModel):

    id = models.AutoField(primary_key=True, db_column="id",
                          verbose_name=_(u"Id"))
    field = models.ForeignKey("Field", db_column="feid", null=False,
                              blank=False, verbose_name=_(u"Field"))
    key = models.ForeignKey("Key", db_column="scid", null=False,
                            blank=False, verbose_name=_(u"Key"))
    position = models.IntegerField(db_column="pos", null=False, blank=False,
                                   verbose_name=_(u"Position"))

    class Meta:
        db_table = u"feldschl"
        db_column_prefix = u"fs_"
        unique_together = ("field", "key")
        verbose_name = _(u"Field key")
        verbose_name_plural = _(u"Field keys")


class DefaultField(TimestampModel):

    id = models.AutoField(primary_key=True, db_column="id",
                          verbose_name=_(u"Id"))
    project = models.ForeignKey("Project", db_column="prid", null=False,
                                blank=False, verbose_name=_(u"Project"))
    name = models.CharField(max_length=60, db_column="name", null=False,
                            blank=False, verbose_name=_(u"Name"))
    position = models.IntegerField(db_column="pos", null=True, blank=True,
                                   verbose_name=_(u"Position"))
    short_description = models.CharField(max_length=60, db_column="sf_zuname",
                                         null=False, blank=False,
                                         verbose_name=_(u"Short description"))
    description = models.CharField(max_length=2000, db_column="txt",
                                   null=True, blank=True,
                                   verbose_name=_(u"Description"))
    label = models.CharField(max_length=60, db_column="label", null=False,
                             blank=False, verbose_name=_(u"Label"))
    type = models.ForeignKey("FieldType", db_column="ftid", null=False,
                             blank=False, verbose_name=_(u"Type"))
    precision = models.CharField(max_length=12, db_column="zus1",
                                 null=True, blank=True,
                                 verbose_name=_(u"Precision"))
    scaling = models.CharField(max_length=12, db_column="zus2",
                               null=True, blank=True,
                               verbose_name=_(u"Scaling"))
    primary = models.BooleanField(db_column="prim", null=False, blank=False,
                                  verbose_name=_(u"Primary"))
    foreign = models.ForeignKey("Field", db_column="fremd_feid",
                                null=True, blank=True,
                                on_delete=models.SET_NULL,
                                verbose_name=_(u"Foreign key"))
    lookup = models.CharField(max_length=2, db_column="look",
                              null=True, blank=True, choices=LOOKUP_CHOICES,
                              verbose_name=_(u"Lookup"))
    nullable = models.BooleanField(db_column="null", null=False,
                                   blank=False,
                                   verbose_name=_(u"Nullable"))
    mask_length = models.IntegerField(db_column="mlang", null=False,
                                      blank=False, default=0,
                                      verbose_name=_(u"Mask length"))
    default_value = models.CharField(max_length=32, db_column="default",
                                     null=True, blank=True,
                                     verbose_name=_(u"Default value"))
    cascading_delete = models.BooleanField(db_column="loesch",
                                           default=False,
                                           verbose_name=_(u"Cascading delete"))

    class Meta:
        db_table = u"standardfeld"
        db_column_prefix = u"sf_"
        unique_together = ("project", "name")
        verbose_name = _(u"Default field")
        verbose_name_plural = _(u"Default fields")

    def __unicode__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def full_name(self):
        if self.table.prefix:
            return "%s_%s" % (self.table.prefix, self.name)
        else:
            return self.name

    def full_type(self):
        retval = "%s" % self.type
        if self.precision and self.scaling:
            retval += " (%s, %s)" % (self.precision, self.scaling)
        elif self.precision and not self.scaling:
            retval += " (%s)" % self.precision
        return retval


class Comment(TimestampModel):

    content_type = models.ForeignKey(ContentType, db_column="contenttype")
    object_id = models.PositiveIntegerField(db_column="objectid")
    content_object = generic.GenericForeignKey("content_type", "object_id")
    is_draft = models.BooleanField(db_column="entwurf", default=True,
        verbose_name=_(u"Is draft"))
    text = models.CharField(db_column="txt", max_length=2000,
        verbose_name=_("Text"))

    class Meta:
        db_table = u"kommentar"
        db_column_prefix = u"kom_"
        verbose_name = _("Comment")
        verbose_name_plural = _(u"Comments")
        
        
class StarredItem(BaseModel):
    
    content_type = models.ForeignKey(ContentType, db_column="contenttype")
    object_id = models.PositiveIntegerField(db_column="objectid")
    content_object = generic.GenericForeignKey("content_type", "object_id")
    user = models.ForeignKey(User, blank=True, null=True, editable=False,
                             db_column="userid",
                             related_name="%(class)s_creator",
                             verbose_name=_(u"User"))

    class Meta:
        db_table = u"lesezeichen"
        db_column_prefix = u"lez_"
        verbose_name = _("Starred item")
        verbose_name_plural = _(u"Starred items")
