# Generated by Django 5.2.1 on 2025-05-15 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='transaction_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
