# Generated by Django 5.0.3 on 2024-04-02 02:13

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ugacaci', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PretBancaire',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('montant_demande', models.DecimalField(decimal_places=2, max_digits=10)),
                ('date_demande', models.DateTimeField(default=django.utils.timezone.now)),
                ('statut', models.CharField(default='En attente', max_length=20)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prets_bancaires', to='ugacaci.client')),
            ],
        ),
    ]
