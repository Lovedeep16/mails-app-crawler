# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-19 13:44
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='allUsStates',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('statename', models.CharField(max_length=500)),
                ('statekey', models.CharField(max_length=400)),
            ],
        ),
        migrations.CreateModel(
            name='job',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('job_title', models.CharField(max_length=100)),
                ('job_discription', models.CharField(max_length=4000)),
                ('company_name', models.CharField(blank=True, default='', max_length=50, null=True)),
                ('company_email', models.EmailField(blank=True, default='', max_length=100, null=True)),
                ('send_on_slack', models.CharField(choices=[('0', '0 '), ('1', '1')], max_length=20)),
                ('last_updated', models.CharField(default='', max_length=400)),
                ('job_url', models.CharField(max_length=1000)),
            ],
        ),
        migrations.CreateModel(
            name='keyword_search',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('keyword_name', models.CharField(max_length=50, unique=True)),
                ('last_updated', models.DateTimeField(auto_now_add=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='portal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('portal_name', models.CharField(max_length=100)),
                ('portal_link', models.TextField(validators=[django.core.validators.URLValidator()])),
                ('last_updated', models.DateTimeField(auto_now_add=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='slack_channel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slack_name', models.CharField(max_length=100, verbose_name='Slack Channel Name #')),
                ('channel_ID', models.CharField(max_length=500, verbose_name='Slack Webhooks ID')),
                ('channeltype', models.CharField(choices=[('mail', 'mail'), ('job', 'job')], max_length=50)),
                ('last_updated', models.DateTimeField(auto_now_add=True, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='keyword_search',
            name='slack_channel_con',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jobs.slack_channel'),
        ),
        migrations.AddField(
            model_name='job',
            name='keyword',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jobs.keyword_search'),
        ),
        migrations.AddField(
            model_name='job',
            name='portal_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jobs.portal'),
        ),
        migrations.AddField(
            model_name='job',
            name='state',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jobs.allUsStates'),
        ),
    ]
