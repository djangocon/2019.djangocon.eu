# Generated by Django 2.1.4 on 2019-02-19 20:41

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('invoices', '0005_auto_20190218_2253'),
    ]

    operations = [
        migrations.CreateModel(
            name='TicketbutlerTicket',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ticketbutler_orderid', models.CharField(default='', max_length=32)),
            ],
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='pdf',
        ),
        migrations.AddField(
            model_name='ticketbutlerticket',
            name='invoice',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='invoices.Invoice'),
        ),
        migrations.AddField(
            model_name='ticketbutlerticket',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tickets', to=settings.AUTH_USER_MODEL),
        ),
    ]
