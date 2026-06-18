from django import forms
from .models import MenuItem, Order, Inventory, Staff, Bill, Supplier


class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ['item_name', 'category', 'price', 'availability', 'description', 'image']


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer_name', 'order_type', 'item', 'quantity', 'note', 'status']

class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = [
            "item_name",
            "category",
            "quantity",
            "unit",
            "supplier",
            "status",
            "note",
        ]

        widgets = {
            "item_name": forms.TextInput(attrs={
                "placeholder": "Enter stock item name"
            }),
            "quantity": forms.NumberInput(attrs={
                "placeholder": "Enter quantity",
                "min": "0"
            }),
            "unit": forms.TextInput(attrs={
                "placeholder": "Example: kg, litre, packet"
            }),
            "note": forms.Textarea(attrs={
                "placeholder": "Stock note",
                "rows": 3
            }),
        }


class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['staff_name', 'role', 'phone', 'email', 'salary', 'shift', 'address']


class BillForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = ['customer_name', 'order', 'payment_method', 'discount', 'tax', 'billing_note']



class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = [
            "supplier_name",
            "contact_person",
            "phone_number",
            "email",
            "address",
            "supplies_category",
            "supplied_items",
            "last_purchase_date",
            "note",
        ]

        widgets = {
            "supplier_name": forms.TextInput(attrs={
                "placeholder": "Supplier name"
            }),
            "contact_person": forms.TextInput(attrs={
                "placeholder": "Contact person"
            }),
            "phone_number": forms.TextInput(attrs={
                "placeholder": "Phone number"
            }),
            "email": forms.EmailInput(attrs={
                "placeholder": "Email address"
            }),
            "address": forms.Textarea(attrs={
                "placeholder": "Supplier address",
                "rows": 3
            }),
            "supplied_items": forms.Textarea(attrs={
                "placeholder": "Example: Coffee Beans, Sugar, Paper Cups",
                "rows": 3
            }),
            "last_purchase_date": forms.DateInput(attrs={
                "type": "date"
            }),
            "note": forms.Textarea(attrs={
                "placeholder": "Delivery or supplier note",
                "rows": 3
            }),
        }