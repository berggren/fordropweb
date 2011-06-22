# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'File.graphid'
        db.add_column('report_file', 'graphid', self.gf('django.db.models.fields.IntegerField')(null=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'File.graphid'
        db.delete_column('report_file', 'graphid')


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
            'graphid': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
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
