# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Investigation'
        db.create_table('investigation_investigation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='description', null=True, to=orm['pages.Page'])),
            ('status', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['investigation.Status'], null=True, blank=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='creator', null=True, to=orm['auth.User'])),
            ('timecreated', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('lastupdated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('investigation', ['Investigation'])

        # Adding M2M table for field investigator on 'Investigation'
        db.create_table('investigation_investigation_investigator', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('investigation', models.ForeignKey(orm['investigation.investigation'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('investigation_investigation_investigator', ['investigation_id', 'user_id'])

        # Adding M2M table for field watcher on 'Investigation'
        db.create_table('investigation_investigation_watcher', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('investigation', models.ForeignKey(orm['investigation.investigation'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('investigation_investigation_watcher', ['investigation_id', 'user_id'])

        # Adding M2M table for field reference on 'Investigation'
        db.create_table('investigation_investigation_reference', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('investigation', models.ForeignKey(orm['investigation.investigation'], null=False)),
            ('reference', models.ForeignKey(orm['investigation.reference'], null=False))
        ))
        db.create_unique('investigation_investigation_reference', ['investigation_id', 'reference_id'])

        # Adding M2M table for field pages on 'Investigation'
        db.create_table('investigation_investigation_pages', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('investigation', models.ForeignKey(orm['investigation.investigation'], null=False)),
            ('page', models.ForeignKey(orm['pages.page'], null=False))
        ))
        db.create_unique('investigation_investigation_pages', ['investigation_id', 'page_id'])

        # Adding model 'Reference'
        db.create_table('investigation_reference', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('timecreated', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('lastupdated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('investigation', ['Reference'])

        # Adding model 'Status'
        db.create_table('investigation_status', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('timecreated', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('lastupdated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('investigation', ['Status'])


    def backwards(self, orm):
        
        # Deleting model 'Investigation'
        db.delete_table('investigation_investigation')

        # Removing M2M table for field investigator on 'Investigation'
        db.delete_table('investigation_investigation_investigator')

        # Removing M2M table for field watcher on 'Investigation'
        db.delete_table('investigation_investigation_watcher')

        # Removing M2M table for field reference on 'Investigation'
        db.delete_table('investigation_investigation_reference')

        # Removing M2M table for field pages on 'Investigation'
        db.delete_table('investigation_investigation_pages')

        # Deleting model 'Reference'
        db.delete_table('investigation_reference')

        # Deleting model 'Status'
        db.delete_table('investigation_status')


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
        'investigation.investigation': {
            'Meta': {'object_name': 'Investigation'},
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'creator'", 'null': 'True', 'to': "orm['auth.User']"}),
            'description': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'description'", 'null': 'True', 'to': "orm['pages.Page']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'investigator': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'investigator'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['auth.User']"}),
            'lastupdated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'pages': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'pages'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['pages.Page']"}),
            'reference': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['investigation.Reference']", 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['investigation.Status']", 'null': 'True', 'blank': 'True'}),
            'timecreated': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'watcher': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'investigation.reference': {
            'Meta': {'object_name': 'Reference'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastupdated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'timecreated': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'investigation.status': {
            'Meta': {'object_name': 'Status'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastupdated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'timecreated': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'pages.page': {
            'Meta': {'object_name': 'Page'},
            'content': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastupdated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'timecreated': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['investigation']
