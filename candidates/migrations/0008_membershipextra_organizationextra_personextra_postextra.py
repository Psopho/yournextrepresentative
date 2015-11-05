# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('popolo', '0002_update_models_from_upstream'),
        ('elections', '0003_allow_null_winner_membership_role'),
        ('candidates', '0007_add_result_recorders_group'),
    ]

    operations = [
        migrations.CreateModel(
            name='MembershipExtra',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('base', models.OneToOneField(related_name='extra', to='popolo.Membership')),
                ('election', models.ForeignKey(related_name='candidacies', blank=True, to='elections.Election', null=True)),
                ('party_list_position', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='OrganizationExtra',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('register', models.CharField(max_length=512, blank=True)),
                ('base', models.OneToOneField(related_name='extra', to='popolo.Organization')),
            ],
        ),
        migrations.CreateModel(
            name='PersonExtra',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cv', models.TextField(blank=True)),
                ('program', models.TextField(blank=True)),
                ('versions', models.TextField(blank=True)),
                ('base', models.OneToOneField(related_name='extra', to='popolo.Person')),
            ],
        ),
        migrations.CreateModel(
            name='PostExtra',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('base', models.OneToOneField(related_name='extra', to='popolo.Post')),
                ('candidates_locked', models.BooleanField(default=False)),
                ('elections', models.ManyToManyField(related_name='posts', to='elections.Election')),
            ],
        ),
    ]
