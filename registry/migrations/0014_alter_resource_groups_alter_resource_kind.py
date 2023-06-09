# Generated by Django 4.1.7 on 2023-02-23 12:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registry', '0013_alter_contributor_unique_together'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resource',
            name='groups',
            field=models.ManyToManyField(blank=True, related_name='resources', to='registry.group', verbose_name='Use cases'),
        ),
        migrations.AlterField(
            model_name='resource',
            name='kind',
            field=models.CharField(choices=[('MATERIAL', 'Material'), ('TEST_METHOD', 'Test method'), ('DATA', 'Data')], max_length=100, verbose_name='Type of resource'),
        ),
    ]
