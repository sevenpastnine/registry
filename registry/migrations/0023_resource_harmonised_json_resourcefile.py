# Generated by Django 4.2.11 on 2024-04-02 09:49

from django.db import migrations, models
import django.db.models.deletion
import registry.models


class Migration(migrations.Migration):

    dependencies = [
        ('registry', '0022_resourcecollection'),
    ]

    operations = [
        migrations.AddField(
            model_name='resource',
            name='harmonised_json',
            field=models.JSONField(blank=True, help_text='JSON file containing the harmonised data', null=True, verbose_name='Harmonised JSON data'),
        ),
        migrations.CreateModel(
            name='ResourceFile',
            fields=[
                ('id', models.CharField(default=registry.models.uuid, editable=False, max_length=22, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('file', models.FileField(help_text='File containing data or information on the resource', upload_to=registry.models.resource_file_path)),
                ('resource', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='registry.resource')),
            ],
            options={
                'ordering': ['resource', 'file'],
            },
        ),
    ]
