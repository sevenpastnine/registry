# Generated by Django 4.1.7 on 2023-02-24 10:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registry', '0015_alter_studydesign_groups'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='contributor',
            options={'ordering': ['role__name', 'person']},
        ),
        migrations.AlterModelOptions(
            name='person',
            options={'ordering': ['user__first_name', 'user__last_name'], 'verbose_name_plural': 'People'},
        ),
    ]
