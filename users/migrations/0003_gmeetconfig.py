# Generated by Django 4.1.4 on 2023-02-24 13:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20230120_2208'),
    ]

    operations = [
        migrations.CreateModel(
            name='GmeetConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tutor_id', models.PositiveIntegerField(blank=True, null=True)),
                ('credentials', models.TextField(blank=True, null=True)),
                ('token', models.TextField(blank=True, null=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'gmeet_config_data',
                'ordering': ['-pk'],
                'index_together': {('tutor_id', 'is_deleted')},
            },
        ),
    ]
