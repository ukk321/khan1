# Generated by Django 4.2 on 2024-10-09 12:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0006_subservicesmodel_size_alter_servicemodel_sort_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subservicesmodel',
            name='size',
            field=models.CharField(blank=True, choices=[('2/3 Years', '2/3Y'), ('3/4 Years', '3/4Y'), ('4/5 Years', '4/5Y'), ('5/6 Years', '5/6Y'), ('6/7 Years', '6/7Y'), ('7/8 Years', '7/8Y'), ('8/9 Years', '8/9Y'), ('9/10 Years', '9/10Y'), ('11/12 Years', '11/12Y'), ('Extra Small', 'XS'), ('Small', 'S'), ('Medium', 'M'), ('Large', 'L'), ('Extra Large', 'XL')], default='Small', max_length=20),
        ),
    ]
