# Generated by Django 5.0.3 on 2024-04-02 03:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ugacaci', '0005_rename_date_naissance_pretbancaire_date_rembourssement_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pretbancaire',
            old_name='date_rembourssement',
            new_name='date_remb',
        ),
    ]
