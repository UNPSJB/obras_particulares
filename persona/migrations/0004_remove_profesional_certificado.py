# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-10-28 18:53
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('persona', '0003_profesional_certificado'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profesional',
            name='certificado',
        ),
    ]
