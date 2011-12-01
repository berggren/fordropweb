from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_unicode

class PostManager(models.Manager):
    def for_model(self, model):
        content_type = ContentType.objects.get_for_model(model)
        query_set = self.get_query_set().filter(content_type=content_type)
        if isinstance(model, models.Model):
            query_set = query_set.filter(object_id=force_unicode(model._get_pk_val()))
        return query_set
