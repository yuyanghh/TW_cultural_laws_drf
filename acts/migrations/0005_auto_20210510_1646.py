# Generated by Django 3.2 on 2021-05-10 08:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('acts', '0004_act_valid_state'),
    ]

    operations = [
        migrations.AlterField(
            model_name='act',
            name='amended_at',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='act',
            name='announced_at',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='act',
            name='applied_at',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='act',
            name='legislated_at',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='amended_at',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='announced_at',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='applied_at',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='legislated_at',
            field=models.DateField(blank=True, null=True),
        ),
    ]
