# Generated by Django 3.0.2 on 2020-02-04 13:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0002_auto_20200204_1337'),
    ]

    operations = [
        migrations.AlterField(
            model_name='derivativetrades',
            name='notionalCurrency',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notionalCurrency_Currencies', to='application.Currencies'),
        ),
        migrations.AlterField(
            model_name='derivativetrades',
            name='underlyingCurrency',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='underlyingCurrency_Currencies', to='application.Currencies'),
        ),
    ]
