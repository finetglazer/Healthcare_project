# Generated by Django 4.2.21 on 2025-06-13 02:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MedicalCondition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('severity_level', models.CharField(choices=[('MILD', 'Mild'), ('MODERATE', 'Moderate'), ('SEVERE', 'Severe')], default='MILD', max_length=20)),
                ('recommended_action', models.TextField()),
                ('source_websites', models.JSONField(default=list)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Symptom',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('is_common', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='SpecialistRecommendation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('specialist_type', models.CharField(max_length=100)),
                ('urgency_level', models.CharField(choices=[('LOW', 'Can wait'), ('MEDIUM', 'See doctor soon'), ('HIGH', 'See doctor immediately')], max_length=20)),
                ('notes', models.TextField(blank=True)),
                ('condition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='medical.medicalcondition')),
            ],
        ),
        migrations.CreateModel(
            name='ConditionSymptom',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('probability', models.FloatField(help_text='0.0 to 1.0 - how likely this symptom indicates this condition')),
                ('is_primary', models.BooleanField(default=False)),
                ('condition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='medical.medicalcondition')),
                ('symptom', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='medical.symptom')),
            ],
            options={
                'unique_together': {('condition', 'symptom')},
            },
        ),
    ]
