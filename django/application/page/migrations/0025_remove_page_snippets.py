# Generated by Django 2.1.7 on 2019-06-02 15:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('page', '0024_pageandsnippetrelation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='page',
            name='snippets',
        ),
    ]