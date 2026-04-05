from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0008_sitesettings_homepage_closing_text"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitesettings",
            name="contact_response_time",
            field=models.CharField(
                blank=True,
                default="two working days",
                help_text=(
                    "Response time shown to enquirers on the contact page and confirmation. "
                    "E.g. 'two working days', '24 hours', 'one week'. "
                    "Appears as: 'Enquiries reviewed within …'"
                ),
                max_length=60,
            ),
        ),
    ]
