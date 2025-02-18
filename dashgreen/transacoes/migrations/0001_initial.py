# Generated by Django 5.1.1 on 2024-10-07 19:35

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contas', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Transacao',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('valor', models.DecimalField(decimal_places=2, max_digits=10)),
                ('tipo', models.CharField(choices=[('Aporte', 'Aporte'), ('Retirada', 'Retirada'), ('Aposta', 'Aposta')], max_length=8)),
                ('resultado', models.CharField(blank=True, choices=[('Green', 'Green'), ('Red', 'Red')], max_length=5, null=True)),
                ('odd', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('retorno', models.DecimalField(decimal_places=2, editable=False, max_digits=10, null=True)),
                ('mercado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contas.mercado')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
