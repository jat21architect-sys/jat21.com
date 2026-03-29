from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0006_sitesettings_hero_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitesettings",
            name="nav_name",
            field=models.CharField(
                blank=True,
                default="",
                help_text=(
                    "Shortened form of your practice name for the navigation bar \u2014 "
                    "e.g. 'Strand Architecture' or 'BWK Partnership'. Use this only if your "
                    "full practice name is long and crowds the header. Leave blank to use the "
                    "full name. A logo supersedes both."
                ),
                max_length=30,
            ),
        ),
    ]
