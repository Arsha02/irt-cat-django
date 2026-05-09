from django.db import models


class Item(models.Model):
    item_id = models.CharField(max_length=10)
    question_text = models.TextField()
    a = models.FloatField()
    b = models.FloatField()
    c = models.FloatField()
