from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField
from django.urls import reverse

from read_count.models import ReadCountBeforeZero, ReadDetail


class BlogType(models.Model):
    type_name = models.CharField(max_length=15)

    def __str__(self):
        return self.type_name

class Blog(models.Model, ReadCountBeforeZero):
    title = models.CharField(max_length=50)
    blog_type = models.ForeignKey(BlogType, on_delete=models.CASCADE)
    content = RichTextUploadingField()
    read_details = GenericRelation(ReadDetail)
    auther = models.ForeignKey(User, on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True)
    last_update_time = models.DateTimeField(auto_now=True)

    def get_url(self):
        return reverse('blog_detail', kwargs={'blog_pk': self.pk})

    def get_email(self):
        return self.auther.email

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_time']

