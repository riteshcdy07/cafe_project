from django.contrib import admin
from .models import MenuItem, Order, Inventory, Staff, Bill


admin.site.register(MenuItem)
admin.site.register(Order)
admin.site.register(Inventory)
admin.site.register(Staff)
admin.site.register(Bill)