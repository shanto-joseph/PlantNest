from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('customer_interaction', '0005_remove_blogpost_featured_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='blogpost',
            name='status',
        ),
        migrations.RemoveField(
            model_name='blogpost',
            name='is_published',
        ),
        migrations.RemoveField(
            model_name='videopost',
            name='is_published',
        ),
    ] 