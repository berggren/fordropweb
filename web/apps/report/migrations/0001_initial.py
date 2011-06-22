# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'File'
        db.create_table('report_file', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('filesize', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('filetype', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('datefolder', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('md5', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('sha1', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('sha256', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('timecreated', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('lastupdated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('report', ['File'])

        # Adding model 'UserFile'
        db.create_table('report_userfile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('file', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['report.File'])),
            ('filename', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('reference', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['investigation.Reference'], null=True, blank=True)),
            ('timecreated', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('lastupdated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('report', ['UserFile'])

        # Adding model 'MalwareMhr'
        db.create_table('report_malwaremhr', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('file', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['report.File'])),
            ('percent', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('timecreated_mhr', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('donotexist', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('timecreated', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('lastupdated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('report', ['MalwareMhr'])

        # Adding model 'Report'
        db.create_table('report_report', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['report.TypeReport'])),
            ('value', self.gf('django.db.models.fields.TextField')(null=True)),
            ('md5', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('sha1', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('sha256', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('timecreated', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('lastupdated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('report', ['Report'])

        # Adding model 'UserReport'
        db.create_table('report_userreport', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('report', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['report.Report'])),
            ('reference', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['investigation.Reference'], null=True, blank=True)),
            ('timecreated', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('lastupdated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('report', ['UserReport'])

        # Adding model 'TypeReport'
        db.create_table('report_typereport', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('timecreated', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('lastupdated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('report', ['TypeReport'])


    def backwards(self, orm):
        
        # Deleting model 'File'
        db.delete_table('report_file')

        # Deleting model 'UserFile'
        db.delete_table('report_userfile')

        # Deleting model 'MalwareMhr'
        db.delete_table('report_malwaremhr')

        # Deleting model 'Report'
        db.delete_table('report_report')

        # Deleting model 'UserReport'
        db.delete_table('report_userreport')

        # Deleting model 'TypeReport'
        db.delete_table('report_typereport')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'investigation.reference': {
            'Meta': {'object_name': 'Reference'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastupdated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'timecreated': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'report.file': {
            'Meta': {'object_name': 'File'},
            'datefolder': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'filesize': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'filetype': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastupdated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'md5': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'sha1': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'sha256': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'timecreated': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'report.malwaremhr': {
            'Meta': {'object_name': 'MalwareMhr'},
            'donotexist': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'file': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['report.File']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastupdated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'percent': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'timecreated': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'timecreated_mhr': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'report.report': {
            'Meta': {'object_name': 'Report'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastupdated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'md5': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'sha1': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'sha256': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'timecreated': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['report.TypeReport']"}),
            'value': ('django.db.models.fields.TextField', [], {'null': 'True'})
        },
        'report.typereport': {
            'Meta': {'object_name': 'TypeReport'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastupdated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'timecreated': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'report.userfile': {
            'Meta': {'object_name': 'UserFile'},
            'file': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['report.File']"}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastupdated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'reference': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['investigation.Reference']", 'null': 'True', 'blank': 'True'}),
            'timecreated': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'report.userreport': {
            'Meta': {'object_name': 'UserReport'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastupdated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'reference': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['investigation.Reference']", 'null': 'True', 'blank': 'True'}),
            'report': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['report.Report']"}),
            'timecreated': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['report']
