from django.db import models


class Item(models.Model):
    item_id = models.CharField(max_length=10)
    question_text = models.TextField()
    a = models.FloatField()
    b = models.FloatField()
    c = models.FloatField()


class Response(models.Model):
    student = models.CharField(max_length=100)
    responses = models.JSONField()
