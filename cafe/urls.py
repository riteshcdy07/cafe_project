from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),

    path('home/', views.home, name='home'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('orders/', views.orders, name='orders'),
    path('menu/', views.menu, name='menu'),
    path('billing/', views.billing, name='billing'),
    path('inventory/', views.inventory, name='inventory'),
    path('staff/', views.staff, name='staff'),
    path('reports/', views.reports, name='reports'),

    path('menu/edit/<int:id>/', views.edit_menu, name='edit_menu'),
    path('menu/delete/<int:id>/', views.delete_menu, name='delete_menu'),

    path('orders/edit/<int:id>/', views.edit_order, name='edit_order'),
    path('orders/delete/<int:id>/', views.delete_order, name='delete_order'),


    path('inventory/edit/<int:id>/', views.edit_inventory, name='edit_inventory'),
    path('inventory/delete/<int:id>/', views.delete_inventory, name='delete_inventory'),


    path('staff/edit/<int:id>/', views.edit_staff, name='edit_staff'),
    path('staff/delete/<int:id>/', views.delete_staff, name='delete_staff'),


    path('billing/edit/<int:id>/', views.edit_bill, name='edit_bill'),
    path('billing/delete/<int:id>/', views.delete_bill, name='delete_bill'),

path("menu/toggle-availability/<int:id>/", views.toggle_menu_availability, name="toggle_menu_availability"),
]