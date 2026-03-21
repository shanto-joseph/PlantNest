from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Role, Address

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')

@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'is_admin')
    list_filter = ('is_active', 'date_joined', 'role')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
    readonly_fields = ('date_joined', 'last_login')
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'profile_picture', 'bio')}),
        ('Role & Permissions', {'fields': ('role', 'is_active')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

class AddressInline(admin.TabularInline):
    model = Address
    extra = 0
    fields = ('address_type', 'first_name', 'last_name', 'address_line', 'city', 'state', 'postal_code', 'is_default')

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'address_type', 'first_name', 'last_name', 'city', 'state', 'is_default')
    list_filter = ('address_type', 'country', 'state', 'is_default')
    search_fields = ('user__username', 'first_name', 'last_name', 'city', 'address_line')
    list_editable = ('is_default',)