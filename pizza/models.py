from django.db import models

# Create your models here.
class DateTimeAbstract(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
class User(models.Model):
    name = models.CharField(max_length=100)
    phone = models.IntegerField(unique=True)
    address = models.CharField(max_length=500)

    def __str__(self):
        template = '{0.name} {0.address}'
        return template.format(self)

class Order(DateTimeAbstract):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_id = models.IntegerField()
    order_status = models.CharField(max_length=100)

    def __str__(self):
        return self.order_status
