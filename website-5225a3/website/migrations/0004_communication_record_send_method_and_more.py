# Generated by Django 5.0.1 on 2024-02-22 18:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0003_alter_group_communication_record_group_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='communication_record',
            name='send_method',
            field=models.CharField(default='unknown', max_length=40),
        ),
        migrations.AddField(
            model_name='group_communication_record',
            name='send_method',
            field=models.CharField(default='unknown', max_length=40),
        ),
    ]
