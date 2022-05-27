# Generated by Django 3.0.2 on 2022-05-27 13:11

from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailimages', '0023_add_choose_permissions'),
        ('wagtailcore', '0066_collection_management_permissions'),
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
                ('slug', django_extensions.db.fields.AutoSlugField(blank=True, editable=False, help_text='Unique identifier of menu. Will be populated automatically from title of menu. Change only if needed.', populate_from='title')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MenuItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('title', models.CharField(help_text='Title of menu item that will be displayed', max_length=50)),
                ('link_url', models.CharField(blank=True, help_text='URL to link to, e.g. /accounts/signup (no language prefix, LEAVE BLANK if you want to link to a page instead of a URL)', max_length=500, null=True)),
                ('title_of_submenu', models.CharField(blank=True, help_text='Title of submenu (LEAVE BLANK if there is no custom submenu)', max_length=50, null=True)),
                ('show_when', models.CharField(choices=[('always', 'Always'), ('logged_in', 'When logged in'), ('not_logged_in', 'When not logged in')], default='always', max_length=15)),
                ('icon', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.Image')),
                ('link_page', models.ForeignKey(blank=True, help_text='Page to link to (LEAVE BLANK if you want to link to a URL instead)', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='wagtailcore.Page')),
                ('menu', modelcluster.fields.ParentalKey(help_text='Menu to which this item belongs', on_delete=django.db.models.deletion.CASCADE, related_name='menu_items', to='blog.Menu')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CompanyLogo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
                ('logo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='wagtailimages.Image')),
            ],
        ),
    ]
