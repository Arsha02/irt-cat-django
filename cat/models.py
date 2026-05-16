from django.db import models


class Item(models.Model):
    item_id = models.CharField(max_length=10, primary_key=True)
    question_text = models.TextField()
    options = models.JSONField()
    correct_option = models.CharField(max_length=2)

    a = models.FloatField()
    b = models.FloatField()
    c = models.FloatField()
