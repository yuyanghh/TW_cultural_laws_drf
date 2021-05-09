# Generated by Django 3.2 on 2021-05-09 15:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Act',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=500, unique=True)),
                ('act_type', models.CharField(blank=True, max_length=30)),
                ('legislated_at', models.DateField(blank=True)),
                ('amended_at', models.DateField(blank=True)),
                ('announced_at', models.DateField(blank=True)),
                ('applied_at', models.DateField(blank=True)),
                ('rich_content', models.TextField(blank=True, unique=True)),
                ('keyword', models.TextField(blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('rich_content', models.TextField(blank=True, unique=True)),
                ('chapter_nr', models.IntegerField(blank=True)),
                ('article_nr', models.IntegerField()),
                ('legislated_at', models.DateField(blank=True)),
                ('amended_at', models.DateField(blank=True)),
                ('announced_at', models.DateField(blank=True)),
                ('applied_at', models.DateField(blank=True)),
                ('keyword', models.TextField(blank=True)),
                ('updated_reason', models.TextField(blank=True)),
                ('deliberation_duration', models.IntegerField(blank=True)),
                ('appended_decision', models.TextField(blank=True)),
                ('act', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='acts.act')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Legislation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('procedure_schedule', models.CharField(max_length=30)),
                ('sittings_date', models.DateField()),
                ('gazette', models.TextField(blank=True)),
                ('main_proposer', models.CharField(blank=True, max_length=30)),
                ('related_doc', models.TextField(blank=True)),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='acts.article')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
