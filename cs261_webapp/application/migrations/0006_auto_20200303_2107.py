# Generated by Django 3.0.3 on 2020-03-03 21:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0005_auto_20200223_1329'),
    ]

    operations = [
        migrations.AlterField(
            model_name='derivativetrades',
            name='archived',
            field=models.BooleanField(default=False),
        ),
    ]
