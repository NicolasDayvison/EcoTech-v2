# Generated by Django 5.2.1 on 2025-05-26 09:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pecas',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('componente', models.CharField(max_length=100)),
                ('material', models.CharField(max_length=100)),
                ('peso', models.CharField(max_length=6)),
            ],
        ),
    ]
