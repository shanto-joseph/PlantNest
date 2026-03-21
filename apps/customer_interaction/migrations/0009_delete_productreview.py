# Generated migration to remove ProductReview model

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customer_interaction', '0008_remove_blogpost_is_published_remove_blogpost_status'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ProductReview',
        ),
    ]