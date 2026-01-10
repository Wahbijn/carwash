# wash/migrations/0004_add_created_at_sql.py
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('wash', '0003_booking_created_at_service_description_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                ALTER TABLE wash_booking
                ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT now();
            """,
            reverse_sql="""
                ALTER TABLE wash_booking
                DROP COLUMN IF EXISTS created_at;
            """
        ),
    ]
