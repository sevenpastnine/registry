# Generated by Django 4.1.5 on 2023-01-10 10:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registry', '0002_alter_group_id_alter_license_description_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='organisation',
            name='short_name',
            field=models.CharField(default='', max_length=50, unique=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='organisation',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
