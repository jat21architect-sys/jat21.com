# Generated migration — de-personalise SiteSettings field defaults.
# Removes Jeannot Tsirenge-specific defaults so a fresh install starts
# with blank values that must be set by the new site owner.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sitesettings",
            name="site_name",
            field=models.CharField(default="", max_length=120),
        ),
        migrations.AlterField(
            model_name="sitesettings",
            name="contact_email",
            field=models.EmailField(default="", max_length=254),
        ),
    ]
