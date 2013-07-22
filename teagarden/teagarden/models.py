# -*- coding: utf-8 -*-

"""Model definitions"""

import warnings

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext as _

from django_utils.models import add_default_fields


BOOLEAN_CHOICES = (
    (0, _(u'False')),
    (1, _(u'True'))
)

LOOKUP_CHOICES = (
    (u'L', _(u'Lookup')),
    (u'D', _(u'Detail'))
)


@add_default_fields
class Project(models.Model):

    name = models.CharField(max_length=250, null=False, blank=False,
                            verbose_name=_(u'Name'), unique=True)
    short_description = models.CharField(
        max_length=40, null=True, blank=True,
        verbose_name=_(u'Short description'))
    description = models.CharField(max_length=256, null=True,
                                   blank=True,
                                   verbose_name=_(u'Description'))

    class Meta:
        ordering = ('name',)
        verbose_name = _(u'Project')
        verbose_name_plural = _(u'Projects')

    def __unicode__(self):
        return self.name


@add_default_fields
class Group(models.Model):

    name = models.CharField(max_length=250, blank=False,
                            null=False, verbose_name=_(u'Name'))
    project = models.ForeignKey('Project', blank=False,
                                null=False, verbose_name=_('Project'))

    class Meta:
        ordering = ('name',)
        unique_together = ('project', 'name')
        verbose_name = _(u'Group')
        verbose_name_plural = _(u'Groups')

    def __unicode__(self):
        return self.name


@add_default_fields
class TableType(models.Model):

    name = models.CharField(max_length=15, null=False,
                            blank=False, unique=True,
                            verbose_name=_(u'Name'))
    short_name = models.CharField(max_length=3, null=False, blank=False,
                                  unique=True,
                                  verbose_name=_(u'Short name'))

    class Meta:
        ordering = ('name',)
        verbose_name = _(u'Tabletype')
        verbose_name_plural = _(u'Tabletypes')

    def __unicode__(self):
        return self.name


@add_default_fields
class Table(models.Model):

    name = models.CharField(max_length=30, null=False,
                            blank=False, verbose_name=_(u'Name'))
    prefix = models.CharField(max_length=3, null=True,
                              blank=True, verbose_name=_(u'Prefix'))
    type = models.ForeignKey('TableType', null=False,
                             blank=False, verbose_name=_(u'Type'))
    short_description = models.CharField(
        max_length=40, null=True, blank=True,
        verbose_name=_(u'Short description'))
    description = models.CharField(max_length=2000,
                                   null=True, blank=True,
                                   verbose_name=_(u'Description'))
    project = models.ForeignKey('Project', null=False,
                                blank=False, verbose_name=_(u'Project'))
    group = models.ManyToManyField('Group', verbose_name=_(u'Group'),
                                   blank=True, null=True,
                                   related_name='tables')

    class Meta:
        ordering = ('name',)
        unique_together = ('project', 'name')
        verbose_name = _(u'Table')
        verbose_name_plural = _(u'Tables')

    def __unicode__(self):
        return self.name

    @property
    def foreign_keys(self):
        fields = Field.objects.filter(table=self.id)
        fields = fields.filter(foreign__isnull=False)
        fields = fields.order_by('position')
        return fields


@add_default_fields
class FieldProperty(models.Model):

    position = models.IntegerField(null=False,
                                   verbose_name=_(u'Position'))
    property = models.ForeignKey('Property', null=False,
                                 blank=False,
                                 verbose_name=_(u'Property'))
    field = models.ForeignKey('Field', null=False,
                              blank=False,
                              verbose_name=_(u'Field'))
    value = models.CharField(max_length=256,
                             verbose_name=_(u'Value'))

    class Meta:
        unique_together = ('property', 'field')
        verbose_name = _(u'Field property')
        verbose_name_plural = _(u'Field properties')


@add_default_fields
class FieldType(models.Model):

    name = models.CharField(max_length=15, null=False,
                            blank=False, unique=True,
                            verbose_name=_(u'Name'))
    short_name = models.CharField(max_length=3,
                                  null=False, blank=False, unique=True,
                                  verbose_name=_(u'Short name'))
    precision = models.IntegerField(null=False,
                                    blank=False, default=False,
                                    choices=BOOLEAN_CHOICES,
                                    verbose_name=_(u'Precision'))
    scaling = models.IntegerField(null=False,
                                  blank=False, default=False,
                                  choices=BOOLEAN_CHOICES,
                                  verbose_name=_(u'Scaling'))

    class Meta:
        ordering = ('name',)
        verbose_name = _(u'Fieldtype')
        verbose_name_plural = _(u'Fieldtypes')

    def __unicode__(self):
        return self.name


@add_default_fields
class Field(models.Model):

    name = models.CharField(max_length=60, null=False,
                            blank=False, verbose_name=_(u'Name'))
    position = models.IntegerField(null=True, blank=True,
                                   verbose_name=_(u'Position'))
    short_description = models.CharField(max_length=60,
                                         null=False, blank=False,
                                         verbose_name=_(u'Short description'))
    description = models.CharField(max_length=2000,
                                   null=True, blank=True,
                                   verbose_name=_(u'Description'))
    label = models.CharField(max_length=60, null=False,
                             blank=False, verbose_name=_(u'Label'))
    type = models.ForeignKey('FieldType', null=False,
                             blank=False, verbose_name=_(u'Type'))
    precision = models.CharField(max_length=12,
                                 null=True, blank=True,
                                 verbose_name=_(u'Precision'))
    scaling = models.CharField(max_length=12,
                               null=True, blank=True,
                               verbose_name=_(u'Scaling'))
    primary = models.IntegerField(null=False, blank=False,
                                  choices=BOOLEAN_CHOICES,
                                  verbose_name=_(u'Primary'))
    foreign = models.ForeignKey('self',
                                null=True, blank=True,
                                on_delete=models.SET_NULL,
                                verbose_name=_(u'Foreign key'))
    lookup = models.CharField(max_length=2,
                              null=True, blank=True, choices=LOOKUP_CHOICES,
                              verbose_name=_(u'Lookup?'))
    nullable = models.IntegerField(null=False,
                                   blank=False, choices=BOOLEAN_CHOICES,
                                   verbose_name=_(u'Nullable'))
    mask_length = models.IntegerField(null=False,
                                      blank=False, default=0,
                                      verbose_name=_(u'Mask length'))
    default_value = models.CharField(max_length=32,
                                     null=True, blank=True,
                                     verbose_name=_(u'Default value'))
    cascading_delete = models.IntegerField(default=False,
                                           choices=BOOLEAN_CHOICES,
                                           verbose_name=_(u'Cascading delete'))
    table = models.ForeignKey('Table', null=False,
                              blank=False, related_name='fields',
                              verbose_name=_(u'Table'))

    class Meta:
        ordering = ('position',)
        unique_together = ('name', 'table')
        verbose_name = _(u'Field')
        verbose_name_plural = _(u'Fields')

    def __unicode__(self):
        return self.name

    def full_name(self):
        """Return a qualified name by table and prefix, if given.

        :returns: Name as string
        """
        if self.table.prefix:
            return '%s_%s' % (self.table.prefix, self.name)
        else:
            return self.name

    def full_type(self):
        retval = '%s' % self.type
        if self.precision and self.scaling:
            retval += ' (%s, %s)' % (self.precision, self.scaling)
        elif self.precision and not self.scaling:
            retval += ' (%s)' % self.precision
        return retval

    def set_next_position(self, table=None):
        """Set the next available position for this field.

        :param table: A :class:`Table` instance
        """
        if not table:
            table = self.table
        fields = Field.objects.filter(table=table)
        max = fields.aggregate(models.Max('position'))['position__max'] or 0
        self.position = max + settings.FIELD_POSITION_GAP


@add_default_fields
class Property(models.Model):

    name = models.CharField(max_length=60, blank=False,
                            null=False, verbose_name=_(u'Name'))

    class Meta:
        ordering = ('name',)
        verbose_name = _(u'Property')
        verbose_name_plural = _(u'Properties')

    def __unicode__(self):
        return self.name


@add_default_fields
class Key(models.Model):

    unique = models.IntegerField(default=False,
                                 choices=BOOLEAN_CHOICES,
                                 verbose_name=_(u'Unique'))
    table = models.ForeignKey('Table',
                              verbose_name=_(u'Table'))
    name = models.CharField(max_length=255,
                            verbose_name=_(u'Name'))

    class Meta:
        ordering = ('name',)
        verbose_name = _(u'Key')
        verbose_name_plural = _(u'Keys')

    def __unicode__(self):
        return self.name


@add_default_fields
class FieldKey(models.Model):

    field = models.ForeignKey('Field', null=False,
                              blank=False, verbose_name=_(u'Field'))
    key = models.ForeignKey('Key', null=False,
                            blank=False, verbose_name=_(u'Key'))
    position = models.IntegerField(null=False, blank=False,
                                   verbose_name=_(u'Position'))

    class Meta:
        unique_together = ('field', 'key')
        verbose_name = _(u'Field key')
        verbose_name_plural = _(u'Field keys')
