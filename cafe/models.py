from django.db import models
from decimal import Decimal

class MenuItem(models.Model):
    CATEGORY_CHOICES = [
        ('Coffee', 'Coffee'),
        ('Tea', 'Tea'),
        ('Snacks', 'Snacks'),
        ('Bakery', 'Bakery'),
        ('Cold Drinks', 'Cold Drinks'),
    ]

    item_name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='menu_images/', blank=True, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    availability = models.CharField(
        max_length=20,
        choices=[('Available', 'Available'), ('Not Available', 'Not Available')],
        default='Available'
    )
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.item_name

class Order(models.Model):
    ORDER_TYPE_CHOICES = [
        ('Dine-in', 'Dine-in'),
        ('Takeaway', 'Takeaway'),
        ('Online', 'Online'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Preparing', 'Preparing'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    customer_name = models.CharField(max_length=100, default='Walk-in Customer')

    order_type = models.CharField(
        max_length=20,
        choices=ORDER_TYPE_CHOICES,
        default='Dine-in'
    )

    table_number = models.CharField(
        max_length=20,
        blank=True,
        default=''
    )

    # Old single-item fields kept temporarily for existing records.
    item = models.ForeignKey(
        MenuItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    quantity = models.PositiveIntegerField(default=1)

    note = models.TextField(blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        if self.order_items.exists():
            return sum(
                (order_item.line_total() for order_item in self.order_items.all()),
                Decimal('0.00')
            )

        if self.item:
            return self.item.price * self.quantity

        return Decimal('0.00')

    def __str__(self):
        return f"Order #{self.id} - {self.customer_name}"

class OrderItem(models.Model):
        order = models.ForeignKey(
            Order,
            on_delete=models.CASCADE,
            related_name='order_items'
        )

        menu_item = models.ForeignKey(
            MenuItem,
            on_delete=models.SET_NULL,
            null=True,
            blank=True
        )

        quantity = models.PositiveIntegerField(default=1)

        unit_price = models.DecimalField(
            max_digits=10,
            decimal_places=2,
            default=0
        )

        item_note = models.CharField(
            max_length=200,
            blank=True,
            default=''
        )

        def line_total(self):
            return self.unit_price * self.quantity

        def __str__(self):
            if self.menu_item:
                return f"{self.menu_item.item_name} × {self.quantity}"
            return f"Deleted Item × {self.quantity}"

class Supplier(models.Model):
    CATEGORY_CHOICES = [
        ('Ingredient', 'Ingredient'),
        ('Packaging', 'Packaging'),
        ('Drink Stock', 'Drink Stock'),
        ('Cleaning Item', 'Cleaning Item'),
        ('Other', 'Other'),
    ]

    supplier_name = models.CharField(max_length=150)
    contact_person = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField()
    supplies_category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='Other'
    )
    supplied_items = models.TextField(
        help_text="Example: Coffee Beans, Sugar, Paper Cups"
    )
    last_purchase_date = models.DateField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.supplier_name



class Inventory(models.Model):
    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Low Stock', 'Low Stock'),
        ('Out of Stock', 'Out of Stock'),
    ]

    CATEGORY_CHOICES = [
        ('Ingredient', 'Ingredient'),
        ('Packaging', 'Packaging'),
        ('Drink Stock', 'Drink Stock'),
        ('Cleaning Item', 'Cleaning Item'),
        ('Other', 'Other'),
    ]

    item_name = models.CharField(max_length=100)
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='Other'
    )
    quantity = models.PositiveIntegerField()
    unit = models.CharField(max_length=30)
    supplier_name = models.CharField(max_length=100, blank=True, null=True)
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="inventory_items"
    )
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='Available'
    )
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.item_name

class Staff(models.Model):
    ROLE_CHOICES = [
        ('Manager', 'Manager'),
        ('Cashier', 'Cashier'),
        ('Waiter', 'Waiter'),
        ('Kitchen Staff', 'Kitchen Staff'),
        ('Cleaner', 'Cleaner'),
    ]

    SHIFT_CHOICES = [
        ('Morning', 'Morning'),
        ('Day', 'Day'),
        ('Evening', 'Evening'),
        ('Full Time', 'Full Time'),
    ]

    staff_name = models.CharField(max_length=100, default='Staff Member')
    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default='Waiter'
    )
    phone = models.CharField(max_length=20, default='N/A')
    email = models.EmailField(blank=True, null=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shift = models.CharField(
        max_length=30,
        choices=SHIFT_CHOICES,
        default='Day'
    )
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.staff_name


class Bill(models.Model):
    PAYMENT_CHOICES = [
        ('Cash', 'Cash'),
        ('Card', 'Card'),
        ('QR Payment', 'QR Payment'),
        ('Online', 'Online'),
    ]

    customer_name = models.CharField(max_length=100)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    payment_method = models.CharField(
        max_length=30,
        choices=PAYMENT_CHOICES,
        default='Cash'
    )
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    billing_note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def subtotal(self):
        if self.order:
            return self.order.total_price()
        return 0

    def total_amount(self):
        return self.subtotal() - self.discount + self.tax

    def __str__(self):
        return f"Bill #{self.id} - {self.customer_name}"