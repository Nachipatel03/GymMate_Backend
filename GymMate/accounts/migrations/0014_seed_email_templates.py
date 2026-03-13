from django.db import migrations


def seed_templates(apps, schema_editor):
    EmailTemplate = apps.get_model('accounts', 'EmailTemplate')

    # Read the existing HTML template files
    import os
    templates_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'templates', 'emails'
    )

    # Member Welcome Email
    welcome_path = os.path.join(templates_dir, 'member_creation_email.html')
    with open(welcome_path, 'r', encoding='utf-8') as f:
        welcome_html = f.read()

    EmailTemplate.objects.create(
        slug='member_welcome',
        name='Member Welcome Email',
        subject='Welcome to GymMate! Your Account Credentials',
        html_body=welcome_html
    )

    # Password Reset Email
    reset_path = os.path.join(templates_dir, 'password_reset_email.html')
    with open(reset_path, 'r', encoding='utf-8') as f:
        reset_html = f.read()

    EmailTemplate.objects.create(
        slug='password_reset',
        name='Password Reset Email',
        subject='GymMate - Password Reset Request',
        html_body=reset_html
    )


def reverse_seed(apps, schema_editor):
    EmailTemplate = apps.get_model('accounts', 'EmailTemplate')
    EmailTemplate.objects.filter(slug__in=['member_welcome', 'password_reset']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0013_emailtemplate'),
    ]

    operations = [
        migrations.RunPython(seed_templates, reverse_seed),
    ]
