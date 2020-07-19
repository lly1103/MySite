from django.utils import timezone
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db.models.fields import exceptions

# 阅读统计
class ReadNum(models.Model):
    read_num = models.IntegerField(default=0)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")  # 通过找到content_type 找到 关联的表名, object_id 找到行id

class ReadCountBeforeZero():
    def get_read_num(self):
        try:
            ct = ContentType.objects.get_for_model(self)
            readnum = ReadNum.objects.get(content_type=ct, object_id=self.id)
            return readnum.read_num
        except exceptions.ObjectDoesNotExist:
            return 0

# 每天阅读统计
class ReadDetail(models.Model):
    date = models.DateField(default=timezone.now)
    read_num = models.IntegerField(default=0)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")