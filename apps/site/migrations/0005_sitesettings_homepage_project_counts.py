from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0004_harden_about_profile_template_surface"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitesettings",
            name="homepage_projects_mobile_count",
            field=models.PositiveSmallIntegerField(
                default=3,
                help_text="Max featured projects shown on mobile (up to 639px). Between 1 and 6.",
            ),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="homepage_projects_tablet_count",
            field=models.PositiveSmallIntegerField(
                default=4,
                help_text="Max featured projects shown on tablet (640–959px). Between 1 and 6, at least mobile count.",
            ),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="homepage_projects_desktop_count",
            field=models.PositiveSmallIntegerField(
                default=6,
                help_text="Max featured projects shown on desktop (960px+). Between 1 and 6, at least tablet count.",
            ),
        ),
    ]
