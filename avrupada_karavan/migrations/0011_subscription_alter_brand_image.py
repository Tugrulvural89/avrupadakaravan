# Generated by Django 4.2.7 on 2023-12-08 13:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('avrupada_karavan', '0010_brand_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AlterField(
            model_name='brand',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='brand_images/'),
        ),
    ]
