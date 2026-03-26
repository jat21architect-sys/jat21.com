from django.db import migrations, models


def forwards(apps, schema_editor):
    AboutProfile = apps.get_model("core", "AboutProfile")
    SiteSettings = apps.get_model("core", "SiteSettings")

    site = SiteSettings.objects.filter(pk=1).first()

    for profile in AboutProfile.objects.all():
        summary_parts = [profile.practice_summary.strip()] if profile.practice_summary.strip() else []
        biography = (profile.biography or "").strip()
        if biography and biography not in summary_parts:
            summary_parts.append(biography)
        profile.practice_summary = "\n\n".join(summary_parts)

        if site and not site.location and (profile.location or "").strip():
            site.location = profile.location.strip()
            site.save(update_fields=["location"])

        profile.portrait_mode = "portrait" if profile.portrait else "text_only"
        profile.save(update_fields=["practice_summary", "portrait_mode"])


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0003_alter_aboutprofile_experience_years"),
    ]

    operations = [
        migrations.RenameField(
            model_name="aboutprofile",
            old_name="headline",
            new_name="one_line_practice_description",
        ),
        migrations.RenameField(
            model_name="aboutprofile",
            old_name="intro",
            new_name="practice_summary",
        ),
        migrations.RenameField(
            model_name="aboutprofile",
            old_name="philosophy",
            new_name="approach",
        ),
        migrations.RenameField(
            model_name="aboutprofile",
            old_name="credentials",
            new_name="supporting_facts",
        ),
        migrations.AlterField(
            model_name="aboutprofile",
            name="one_line_practice_description",
            field=models.CharField(
                blank=True,
                help_text="Short public description shown in the hero.",
                max_length=220,
            ),
        ),
        migrations.AlterField(
            model_name="aboutprofile",
            name="practice_summary",
            field=models.TextField(
                blank=True,
                help_text="Short factual summary of what the practice does, where it is based, and the kind of work it takes on.",
            ),
        ),
        migrations.AlterField(
            model_name="aboutprofile",
            name="approach",
            field=models.TextField(
                blank=True,
                help_text="Keep this practical and brief — ideally 2 to 3 sentences.",
            ),
        ),
        migrations.AlterField(
            model_name="aboutprofile",
            name="supporting_facts",
            field=models.TextField(
                blank=True,
                help_text="Concrete supporting facts — one per line. Use factual proof, not positioning language.",
            ),
        ),
        migrations.AddField(
            model_name="aboutprofile",
            name="identity_mode",
            field=models.CharField(
                choices=[("person", "Person-led practice"), ("studio", "Studio-led practice")],
                default="studio",
                help_text="Choose whether the About page should introduce a named principal or the studio as a whole.",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="aboutprofile",
            name="principal_name",
            field=models.CharField(
                blank=True,
                help_text="Required for person-led practices. Leave blank for studio-led practices.",
                max_length=120,
            ),
        ),
        migrations.AddField(
            model_name="aboutprofile",
            name="principal_title",
            field=models.CharField(
                blank=True,
                help_text="Examples: Founder and Registered Architect, Principal Architect.",
                max_length=120,
            ),
        ),
        migrations.AddField(
            model_name="aboutprofile",
            name="practice_structure",
            field=models.CharField(
                blank=True,
                help_text="A short truthful descriptor such as 'Solo practice' or 'Small studio'.",
                max_length=120,
            ),
        ),
        migrations.AddField(
            model_name="aboutprofile",
            name="project_leadership",
            field=models.TextField(
                blank=True,
                help_text="Explain how projects are led and how consultants or collaborators are involved.",
            ),
        ),
        migrations.AddField(
            model_name="aboutprofile",
            name="professional_standing",
            field=models.CharField(
                blank=True,
                help_text="Registration or professional standing shown publicly on the About page.",
                max_length=220,
            ),
        ),
        migrations.AddField(
            model_name="aboutprofile",
            name="education",
            field=models.TextField(blank=True, help_text="Education details \u2014 one per line."),
        ),
        migrations.AddField(
            model_name="aboutprofile",
            name="closing_invitation",
            field=models.CharField(
                blank=True,
                help_text="Short closing invitation shown above the contact CTA.",
                max_length=220,
            ),
        ),
        migrations.AddField(
            model_name="aboutprofile",
            name="portrait_mode",
            field=models.CharField(
                choices=[("portrait", "Show portrait"), ("text_only", "Text only")],
                default="text_only",
                help_text="Use text-only mode until a real portrait is ready. Public gray placeholders are intentionally disabled.",
                max_length=20,
            ),
        ),
        migrations.RunPython(forwards, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="aboutprofile",
            name="biography",
        ),
        migrations.RemoveField(
            model_name="aboutprofile",
            name="location",
        ),
    ]
