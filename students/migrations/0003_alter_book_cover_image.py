# Generated by Django 5.0.4 on 2025-02-05 13:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0002_alter_book_cover_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='cover_image',
            field=models.ImageField(blank=True, null=True, upload_to='book/%Y/%m/', verbose_name='Bìa sách'),
        ),
    ]
