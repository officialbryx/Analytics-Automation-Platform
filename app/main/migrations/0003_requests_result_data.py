from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_requests_sheet_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='requests',
            name='result_data',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
