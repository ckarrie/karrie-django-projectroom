# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-11-13 15:56
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ('projectroom', '0003_auto_20181101_1206'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='company',
            name='slug',
        ),
        migrations.RemoveField(
            model_name='jobtype',
            name='slug',
        ),
        migrations.AlterField(
            model_name='account',
            name='balance',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, verbose_name=b'Kontostand'),
        ),
        migrations.AlterField(
            model_name='job',
            name='account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projectroom.Account', verbose_name='Konto'),
        ),
        migrations.AlterField(
            model_name='job',
            name='deadline',
            field=models.DateTimeField(verbose_name='Frist'),
        ),
        migrations.AlterField(
            model_name='job',
            name='description',
            field=models.TextField(verbose_name='Beschreibung'),
        ),
        migrations.AlterField(
            model_name='job',
            name='job_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projectroom.JobType', verbose_name='Auftragstyp'),
        ),
        migrations.AlterField(
            model_name='job',
            name='name',
            field=models.CharField(max_length=255, verbose_name='Auftragstitel'),
        ),
        migrations.AlterField(
            model_name='job',
            name='parent',
            field=mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='projectroom.Job', verbose_name='\xdcbergeordneter Auftrag'),
        ),
        migrations.AlterField(
            model_name='job',
            name='rate',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projectroom.Rate', verbose_name='Tarif'),
        ),
        migrations.AlterField(
            model_name='job',
            name='request_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Anfrage vom'),
        ),
        migrations.AlterField(
            model_name='job',
            name='request_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projectroom.Person', verbose_name='Anfrage von'),
        ),
        migrations.AlterField(
            model_name='person',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='assigned_to',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='assigned_tickets', to='projectroom.Person', verbose_name='Zuweisen an'),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='duration_post',
            field=models.IntegerField(blank=True, null=True, verbose_name='tats\xe4chlicher Aufwand'),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='duration_pre',
            field=models.IntegerField(blank=True, null=True, verbose_name='gesch\xe4tzter Aufwand'),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='name',
            field=models.CharField(max_length=255, verbose_name='Ticketname'),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='request_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requested_tickets', to='projectroom.Person', verbose_name='Anfrage von'),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='status',
            field=models.IntegerField(choices=[(1, 'Anfrage von AG'), (2, 'Gesehen von AN'), (3, 'Gestartet von AN'), (4, 'Abgebrochen von AN'), (5, 'Abgebrochen von AG'), (6, 'Warten auf Pr\xfcfung des AG'), (7, 'Gepr\xfcft von AG'), (8, 'AN wartet auf Bezahlung'), (9, 'Beendet von AN')], verbose_name='Status'),
        ),
    ]
