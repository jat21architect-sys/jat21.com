from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0005_sitesettings_homepage_project_counts"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitesettings",
            name="hero_label",
            field=models.CharField(
                blank=True,
                default="",
                help_text=(
                    "Short descriptor shown above the studio name in the homepage hero "
                    "(e.g. 'Architecture & Urbanism'). Leave blank to omit."
                ),
                max_length=60,
            ),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="hero_compact",
            field=models.BooleanField(
                default=False,
                help_text=(
                    "Compact hero text \u2014 use if your practice name or tagline is long "
                    "and the hero looks crowded."
                ),
            ),
        ),
        migrations.AlterField(
            model_name="sitesettings",
            name="site_name",
            field=models.CharField(
                default="",
                help_text=(
                    "Your practice's display name. "
                    "Shorter names (under 40 characters) work best in the homepage hero."
                ),
                max_length=120,
            ),
        ),
        migrations.AlterField(
            model_name="sitesettings",
            name="tagline",
            field=models.CharField(
                blank=True,
                default="Architectural design shaped by context, clarity, and identity.",
                help_text=(
                    "One or two sentences describing your practice. "
                    "Under 140 characters fits most hero layouts cleanly."
                ),
                max_length=220,
            ),
        ),
    ]
