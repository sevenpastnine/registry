# Generated by Django 4.1.7 on 2023-02-24 11:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registry', '0016_alter_contributor_options_alter_person_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='orcid',
            field=models.CharField(blank=True, max_length=19, null=True, verbose_name='ORCID Id'),
        ),
    ]
