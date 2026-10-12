from django.contrib import admin
from .models import Order, OrderItem
# Register your models here.




class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'customer_name',
        'total_amount',
        'status',
        'created_at'
    )

    list_filter = ('status',)
    inlines = [OrderItemInline]