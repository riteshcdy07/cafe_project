import json
from django.shortcuts import render, redirect, get_object_or_404
from .models import MenuItem, Order, OrderItem, Inventory, Staff, Bill, Supplier
from .forms import MenuItemForm, OrderForm, InventoryForm, StaffForm, BillForm, SupplierForm
from decimal import Decimal
from django.contrib.auth.decorators import login_required, user_passes_test

def is_admin_or_manager(user):
    return user.is_superuser or user.groups.filter(name__in=["Admin", "Manager"]).exists()

def home(request):

    return render(request, "cafe/home.html")


def dashboard(request):
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status="Pending").count()
    completed_orders = Order.objects.filter(status="Completed").count()

    total_menu = MenuItem.objects.count()
    total_inventory = Inventory.objects.count()
    low_stock_count = Inventory.objects.filter(status="Low Stock").count()
    out_stock_count = Inventory.objects.filter(status="Out of Stock").count()

    total_staff = Staff.objects.count()
    total_bills = Bill.objects.count()

    bills = Bill.objects.all()
    total_sales = sum(bill.total_amount() for bill in bills)

    recent_orders = Order.objects.all().order_by("-created_at")[:5]
    recent_bills = Bill.objects.all().order_by("-created_at")[:5]
    stock_alerts = Inventory.objects.filter(status__in=["Low Stock", "Out of Stock"]).order_by("-id")[:5]

    context = {
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "completed_orders": completed_orders,
        "total_menu": total_menu,
        "total_inventory": total_inventory,
        "low_stock_count": low_stock_count,
        "out_stock_count": out_stock_count,
        "total_staff": total_staff,
        "total_bills": total_bills,
        "total_sales": total_sales,
        "recent_orders": recent_orders,
        "recent_bills": recent_bills,
        "stock_alerts": stock_alerts,
    }

    return render(request, "cafe/dashboard.html", context)

def orders(request):
    selected_status = request.GET.get("status")

    valid_statuses = ["Pending", "Preparing", "Completed", "Cancelled"]

    order_records = Order.objects.all().order_by("-created_at")

    menu_items = MenuItem.objects.filter(
        availability="Available"
    ).order_by("category", "item_name")

    if selected_status in valid_statuses:
        order_records = order_records.filter(status=selected_status)

    kitchen_orders = Order.objects.filter(
        status__in=["Pending", "Preparing"]
    ).order_by("created_at")

    billed_order_ids = Bill.objects.filter(
        order__isnull=False
    ).values_list("order_id", flat=True)

    billing_ready_orders = Order.objects.filter(
        status="Completed"
    ).exclude(
        id__in=billed_order_ids
    ).order_by("-created_at")

    pending_count = Order.objects.filter(status="Pending").count()
    preparing_count = Order.objects.filter(status="Preparing").count()
    completed_count = Order.objects.filter(status="Completed").count()
    cancelled_count = Order.objects.filter(status="Cancelled").count()

    form = OrderForm()

    if request.method == "POST":
        cart_data = request.POST.get("cart_data")

        if cart_data:
            cart_items = json.loads(cart_data)

            customer_name = request.POST.get("customer_name", "Walk-in Customer")
            order_type = request.POST.get("order_type", "Dine-in")
            table_number = request.POST.get("table_number", "")
            note = request.POST.get("note", "")

            if cart_items:
                order = Order.objects.create(
                    customer_name=customer_name,
                    order_type=order_type,
                    table_number=table_number,
                    note=note,
                    status="Pending"
                )

                first_item = None
                total_quantity = 0

                for cart_item in cart_items:
                    menu_item = get_object_or_404(MenuItem, id=cart_item["id"])

                    quantity = int(cart_item["quantity"])
                    total_quantity += quantity

                    OrderItem.objects.create(
                        order=order,
                        menu_item=menu_item,
                        quantity=quantity,
                        unit_price=menu_item.price
                    )

                    if first_item is None:
                        first_item = menu_item

                order.item = first_item
                order.quantity = total_quantity
                order.save()

                return redirect("orders")

        form = OrderForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("orders")

    context = {
        "orders": order_records,
        "menu_items": menu_items,
        "kitchen_orders": kitchen_orders,
        "billing_ready_orders": billing_ready_orders,
        "form": form,
        "selected_status": selected_status,
        "pending_count": pending_count,
        "preparing_count": preparing_count,
        "completed_count": completed_count,
        "cancelled_count": cancelled_count,
    }

    return render(request, "cafe/orders.html", context)
def staff(request):
    staff_members = Staff.objects.all().order_by("-id")

    total_staff = Staff.objects.count()
    manager_count = Staff.objects.filter(role="Manager").count()
    cashier_count = Staff.objects.filter(role="Cashier").count()
    waiter_count = Staff.objects.filter(role="Waiter").count()
    kitchen_count = Staff.objects.filter(role="Kitchen Staff").count()

    if request.method == "POST":
        form = StaffForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("staff")
    else:
        form = StaffForm()

    context = {
        "staff_members": staff_members,
        "form": form,
        "total_staff": total_staff,
        "manager_count": manager_count,
        "cashier_count": cashier_count,
        "waiter_count": waiter_count,
        "kitchen_count": kitchen_count,
    }

    return render(request, "cafe/staff.html", context)


@login_required
@user_passes_test(is_admin_or_manager)
def menu(request):
    selected_category = request.GET.get("category")

    if selected_category:
        menu_items = MenuItem.objects.filter(category=selected_category).order_by("-id")
    else:
        menu_items = MenuItem.objects.all().order_by("-id")

    if request.method == "POST":
        form = MenuItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("menu")
    else:
        form = MenuItemForm()

    context = {
        "menu_items": menu_items,
        "form": form,
        "selected_category": selected_category,
    }

    return render(request, "cafe/menu.html", context)

def toggle_menu_availability(request, id):
    item = get_object_or_404(MenuItem, id=id)

    if item.availability == "Available":
        item.availability = "Not Available"
    else:
        item.availability = "Available"

    item.save()
    return redirect("menu")



def billing(request):
    bills = Bill.objects.all().order_by("-created_at")

    selected_order_id = request.GET.get("order")
    initial_data = {}

    if selected_order_id:
        selected_order = get_object_or_404(
            Order,
            id=selected_order_id,
            status="Completed"
        )

        # Do not allow an already billed order to be opened again for billing
        if Bill.objects.filter(order=selected_order).exists():
            return redirect("billing")

        initial_data = {
            "customer_name": selected_order.customer_name,
            "order": selected_order,
        }

    if request.method == "POST":
        form = BillForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("billing")
    else:
        form = BillForm(initial=initial_data)

    context = {
        "bills": bills,
        "form": form,
    }

    return render(request, "cafe/billing.html", context)


def reports(request):
    selected_tab = request.GET.get("tab", "Overview")

    valid_tabs = ["Overview", "Sales", "Orders", "Inventory", "Staff"]

    if selected_tab not in valid_tabs:
        selected_tab = "Overview"

    # Billing / Sales Data
    bills = Bill.objects.select_related("order", "order__item").all().order_by("-created_at")
    total_bills = bills.count()

    total_sales = sum(
        (bill.total_amount() for bill in bills),
        Decimal("0.00")
    )

    cash_sales = sum(
        (bill.total_amount() for bill in bills.filter(payment_method="Cash")),
        Decimal("0.00")
    )

    qr_sales = sum(
        (bill.total_amount() for bill in bills.filter(payment_method="QR Payment")),
        Decimal("0.00")
    )

    # Order Report Data
    order_records = Order.objects.select_related("item").all().order_by("-created_at")
    total_orders = order_records.count()
    pending_orders = order_records.filter(status="Pending").count()
    preparing_orders = order_records.filter(status="Preparing").count()
    completed_orders = order_records.filter(status="Completed").count()
    cancelled_orders = order_records.filter(status="Cancelled").count()

    # Inventory Report Data
    inventory_items = Inventory.objects.select_related("supplier").all().order_by("-id")
    total_inventory = inventory_items.count()
    available_stock = inventory_items.filter(status="Available").count()
    low_stock = inventory_items.filter(status="Low Stock").count()
    out_of_stock = inventory_items.filter(status="Out of Stock").count()

    # Staff Report Data
    staff_members = Staff.objects.all().order_by("-id")
    total_staff = staff_members.count()
    managers = staff_members.filter(role="Manager").count()
    cashiers = staff_members.filter(role="Cashier").count()
    waiters = staff_members.filter(role="Waiter").count()
    kitchen_staff = staff_members.filter(role="Kitchen Staff").count()

    context = {
        "selected_tab": selected_tab,

        "bills": bills,
        "total_bills": total_bills,
        "total_sales": total_sales,
        "cash_sales": cash_sales,
        "qr_sales": qr_sales,

        "order_records": order_records,
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "preparing_orders": preparing_orders,
        "completed_orders": completed_orders,
        "cancelled_orders": cancelled_orders,

        "inventory_items": inventory_items,
        "total_inventory": total_inventory,
        "available_stock": available_stock,
        "low_stock": low_stock,
        "out_of_stock": out_of_stock,

        "staff_members": staff_members,
        "total_staff": total_staff,
        "managers": managers,
        "cashiers": cashiers,
        "waiters": waiters,
        "kitchen_staff": kitchen_staff,
    }

    return render(request, "cafe/reports.html", context)

def inventory(request):
    inventory_items = Inventory.objects.all().order_by("-id")
    suppliers = Supplier.objects.all().order_by("-id")

    total_items = Inventory.objects.count()
    low_stock_count = Inventory.objects.filter(status="Low Stock").count()
    available_count = Inventory.objects.filter(status="Available").count()
    out_stock_count = Inventory.objects.filter(status="Out of Stock").count()

    inventory_form = InventoryForm()
    supplier_form = SupplierForm()

    if request.method == "POST":
        form_type = request.POST.get("form_type", "inventory")

        if form_type == "supplier":
            supplier_form = SupplierForm(request.POST)

            if supplier_form.is_valid():
                supplier_form.save()
                return redirect("inventory")

        else:
            inventory_form = InventoryForm(request.POST)

            if inventory_form.is_valid():
                inventory_form.save()
                return redirect("inventory")

    context = {
        "inventory_items": inventory_items,
        "suppliers": suppliers,
        "form": inventory_form,
        "supplier_form": supplier_form,
        "total_items": total_items,
        "low_stock_count": low_stock_count,
        "available_count": available_count,
        "out_stock_count": out_stock_count,
    }

    return render(request, "cafe/inventory.html", context)

# for edit and delete menu
def edit_menu(request, id):
    item = get_object_or_404(MenuItem, id=id)

    if request.method == "POST":
        form = MenuItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            return redirect("menu")
    else:
        form = MenuItemForm(instance=item)

    context = {
        "form": form,
        "item": item,
    }

    return render(request, "cafe/edit_menu.html", context)


def delete_menu(request, id):
    item = get_object_or_404(MenuItem, id=id)

    if request.method == "POST":
        item.delete()
        return redirect("menu")

    context = {
        "item": item,
    }

    return render(request, "cafe/delete_menu.html", context)


# for edit and delete order
def edit_order(request, id):
    order = get_object_or_404(Order, id=id)

    if request.method == "POST":
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect("orders")

    else:
        form = OrderForm(instance=order)

        context = {
            "form": form,
            "order": order,
        }

        return render(request, "cafe/edit_order.html", context)

def delete_order(request, id):
    order = get_object_or_404(Order, id=id)

    if request.method == "POST":
        order.delete()
        return redirect("orders")

    context = {
        "order": order,
    }

    return render(request, "cafe/delete_order.html", context)

# for edit and delete inventory
def edit_inventory(request, id):
    item = get_object_or_404(Inventory, id=id)

    if request.method == "POST":
        form = InventoryForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect("inventory")
    else:
        form = InventoryForm(instance=item)

    context = {
        "form": form,
        "item": item,
    }

    return render(request, "cafe/edit_inventory.html", context)


def delete_inventory(request, id):
    item = get_object_or_404(Inventory, id=id)

    if request.method == "POST":
        item.delete()
        return redirect("inventory")

    context = {
        "item": item,
    }

    return render(request, "cafe/delete_inventory.html", context)

# for edit and delete staff
def edit_staff(request, id):
    staff_member = get_object_or_404(Staff, id=id)

    if request.method == "POST":
        form = StaffForm(request.POST, instance=staff_member)
        if form.is_valid():
            form.save()
            return redirect("staff")
    else:
        form = StaffForm(instance=staff_member)

    context = {
        "form": form,
        "staff_member": staff_member,
    }

    return render(request, "cafe/edit_staff.html", context)


def delete_staff(request, id):
    staff_member = get_object_or_404(Staff, id=id)

    if request.method == "POST":
        staff_member.delete()
        return redirect("staff")

    context = {
        "staff_member": staff_member,
    }

    return render(request, "cafe/delete_staff.html", context)


# for edit and delete bill
def edit_bill(request, id):
    bill = get_object_or_404(Bill, id=id)

    if request.method == "POST":
        form = BillForm(request.POST, instance=bill)
        if form.is_valid():
            form.save()
            return redirect("billing")
    else:
        form = BillForm(instance=bill)

    context = {
        "form": form,
        "bill": bill,
    }

    return render(request, "cafe/edit_bill.html", context)


def delete_bill(request, id):
    bill = get_object_or_404(Bill, id=id)

    if request.method == "POST":
        bill.delete()
        return redirect("billing")

    context = {
        "bill": bill,
    }

    return render(request, "cafe/delete_bill.html", context)