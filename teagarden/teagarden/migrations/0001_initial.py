# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Project'
        db.create_table(u'teagarden_project', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=250)),
            ('short_description', self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('modified_by', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal(u'teagarden', ['Project'])

        # Adding model 'Group'
        db.create_table(u'teagarden_group', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['teagarden.Project'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('modified_by', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal(u'teagarden', ['Group'])

        # Adding unique constraint on 'Group', fields ['project', 'name']
        db.create_unique(u'teagarden_group', ['project_id', 'name'])

        # Adding model 'TableType'
        db.create_table(u'teagarden_tabletype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=15)),
            ('short_name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=3)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('modified_by', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal(u'teagarden', ['TableType'])

        # Adding model 'Table'
        db.create_table(u'teagarden_table', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('prefix', self.gf('django.db.models.fields.CharField')(max_length=3, null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['teagarden.TableType'])),
            ('short_description', self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=2000, null=True, blank=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['teagarden.Project'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('modified_by', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal(u'teagarden', ['Table'])

        # Adding unique constraint on 'Table', fields ['project', 'name']
        db.create_unique(u'teagarden_table', ['project_id', 'name'])

        # Adding M2M table for field group on 'Table'
        db.create_table(u'teagarden_table_group', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('table', models.ForeignKey(orm[u'teagarden.table'], null=False)),
            ('group', models.ForeignKey(orm[u'teagarden.group'], null=False))
        ))
        db.create_unique(u'teagarden_table_group', ['table_id', 'group_id'])

        # Adding model 'FieldProperty'
        db.create_table(u'teagarden_fieldproperty', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('position', self.gf('django.db.models.fields.IntegerField')()),
            ('property', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['teagarden.Property'])),
            ('field', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['teagarden.Field'])),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('modified_by', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal(u'teagarden', ['FieldProperty'])

        # Adding unique constraint on 'FieldProperty', fields ['property', 'field']
        db.create_unique(u'teagarden_fieldproperty', ['property_id', 'field_id'])

        # Adding model 'FieldType'
        db.create_table(u'teagarden_fieldtype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=15)),
            ('short_name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=3)),
            ('precision', self.gf('django.db.models.fields.IntegerField')(default=False)),
            ('scaling', self.gf('django.db.models.fields.IntegerField')(default=False)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('modified_by', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal(u'teagarden', ['FieldType'])

        # Adding model 'Field'
        db.create_table(u'teagarden_field', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('position', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('short_description', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=2000, null=True, blank=True)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['teagarden.FieldType'])),
            ('precision', self.gf('django.db.models.fields.CharField')(max_length=12, null=True, blank=True)),
            ('scaling', self.gf('django.db.models.fields.CharField')(max_length=12, null=True, blank=True)),
            ('primary', self.gf('django.db.models.fields.IntegerField')()),
            ('foreign', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['teagarden.Field'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('lookup', self.gf('django.db.models.fields.CharField')(max_length=2, null=True, blank=True)),
            ('nullable', self.gf('django.db.models.fields.IntegerField')()),
            ('mask_length', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('default_value', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('cascading_delete', self.gf('django.db.models.fields.IntegerField')(default=False)),
            ('table', self.gf('django.db.models.fields.related.ForeignKey')(related_name='fields', to=orm['teagarden.Table'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('modified_by', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal(u'teagarden', ['Field'])

        # Adding unique constraint on 'Field', fields ['name', 'table']
        db.create_unique(u'teagarden_field', ['name', 'table_id'])

        # Adding model 'Property'
        db.create_table(u'teagarden_property', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('modified_by', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal(u'teagarden', ['Property'])

        # Adding model 'Key'
        db.create_table(u'teagarden_key', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('unique', self.gf('django.db.models.fields.IntegerField')(default=False)),
            ('table', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['teagarden.Table'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('modified_by', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal(u'teagarden', ['Key'])

        # Adding model 'FieldKey'
        db.create_table(u'teagarden_fieldkey', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('field', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['teagarden.Field'])),
            ('key', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['teagarden.Key'])),
            ('position', self.gf('django.db.models.fields.IntegerField')()),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('modified_by', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal(u'teagarden', ['FieldKey'])

        # Adding unique constraint on 'FieldKey', fields ['field', 'key']
        db.create_unique(u'teagarden_fieldkey', ['field_id', 'key_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'FieldKey', fields ['field', 'key']
        db.delete_unique(u'teagarden_fieldkey', ['field_id', 'key_id'])

        # Removing unique constraint on 'Field', fields ['name', 'table']
        db.delete_unique(u'teagarden_field', ['name', 'table_id'])

        # Removing unique constraint on 'FieldProperty', fields ['property', 'field']
        db.delete_unique(u'teagarden_fieldproperty', ['property_id', 'field_id'])

        # Removing unique constraint on 'Table', fields ['project', 'name']
        db.delete_unique(u'teagarden_table', ['project_id', 'name'])

        # Removing unique constraint on 'Group', fields ['project', 'name']
        db.delete_unique(u'teagarden_group', ['project_id', 'name'])

        # Deleting model 'Project'
        db.delete_table(u'teagarden_project')

        # Deleting model 'Group'
        db.delete_table(u'teagarden_group')

        # Deleting model 'TableType'
        db.delete_table(u'teagarden_tabletype')

        # Deleting model 'Table'
        db.delete_table(u'teagarden_table')

        # Removing M2M table for field group on 'Table'
        db.delete_table('teagarden_table_group')

        # Deleting model 'FieldProperty'
        db.delete_table(u'teagarden_fieldproperty')

        # Deleting model 'FieldType'
        db.delete_table(u'teagarden_fieldtype')

        # Deleting model 'Field'
        db.delete_table(u'teagarden_field')

        # Deleting model 'Property'
        db.delete_table(u'teagarden_property')

        # Deleting model 'Key'
        db.delete_table(u'teagarden_key')

        # Deleting model 'FieldKey'
        db.delete_table(u'teagarden_fieldkey')


    models = {
        u'teagarden.field': {
            'Meta': {'ordering': "('position',)", 'unique_together': "(('name', 'table'),)", 'object_name': 'Field'},
            'cascading_delete': ('django.db.models.fields.IntegerField', [], {'default': 'False'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'default_value': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '2000', 'null': 'True', 'blank': 'True'}),
            'foreign': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['teagarden.Field']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'lookup': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'mask_length': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'modified_by': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'nullable': ('django.db.models.fields.IntegerField', [], {}),
            'position': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'precision': ('django.db.models.fields.CharField', [], {'max_length': '12', 'null': 'True', 'blank': 'True'}),
            'primary': ('django.db.models.fields.IntegerField', [], {}),
            'scaling': ('django.db.models.fields.CharField', [], {'max_length': '12', 'null': 'True', 'blank': 'True'}),
            'short_description': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'table': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fields'", 'to': u"orm['teagarden.Table']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['teagarden.FieldType']"})
        },
        u'teagarden.fieldkey': {
            'Meta': {'unique_together': "(('field', 'key'),)", 'object_name': 'FieldKey'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'field': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['teagarden.Field']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['teagarden.Key']"}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'modified_by': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'position': ('django.db.models.fields.IntegerField', [], {})
        },
        u'teagarden.fieldproperty': {
            'Meta': {'unique_together': "(('property', 'field'),)", 'object_name': 'FieldProperty'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'field': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['teagarden.Field']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'modified_by': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'position': ('django.db.models.fields.IntegerField', [], {}),
            'property': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['teagarden.Property']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'teagarden.fieldtype': {
            'Meta': {'ordering': "('name',)", 'object_name': 'FieldType'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'modified_by': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '15'}),
            'precision': ('django.db.models.fields.IntegerField', [], {'default': 'False'}),
            'scaling': ('django.db.models.fields.IntegerField', [], {'default': 'False'}),
            'short_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '3'})
        },
        u'teagarden.group': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('project', 'name'),)", 'object_name': 'Group'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'modified_by': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['teagarden.Project']"})
        },
        u'teagarden.key': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Key'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'modified_by': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'table': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['teagarden.Table']"}),
            'unique': ('django.db.models.fields.IntegerField', [], {'default': 'False'})
        },
        u'teagarden.project': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Project'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'modified_by': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '250'}),
            'short_description': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'})
        },
        u'teagarden.property': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Property'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'modified_by': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'})
        },
        u'teagarden.table': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('project', 'name'),)", 'object_name': 'Table'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '2000', 'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'tables'", 'symmetrical': 'False', 'to': u"orm['teagarden.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'modified_by': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'prefix': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['teagarden.Project']"}),
            'short_description': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['teagarden.TableType']"})
        },
        u'teagarden.tabletype': {
            'Meta': {'ordering': "('name',)", 'object_name': 'TableType'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'modified_by': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '15'}),
            'short_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '3'})
        }
    }

    complete_apps = ['teagarden']