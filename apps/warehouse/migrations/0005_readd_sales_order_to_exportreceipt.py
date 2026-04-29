
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0002_remove_warehousetransaction_warehouse_and_more'),
        ('warehouse', '0004_remove_exportreceipt_sales_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='exportreceipt',
            name='sales_order',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='export_receipts',
                to='order.salesorder',
            ),
        ),
    ]
