# Generated by Django 2.1.7 on 2019-06-02 14:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('page', '0019_page_snippets'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='clean_snippets',
            field=models.TextField(blank=True, editable=False, null=True, verbose_name='Clean snippets'),
        ),
    ]