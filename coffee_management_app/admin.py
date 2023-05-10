from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, AdminManager, Clerk, Coffee_types, Batch, Suppliers, Attendance, AttendanceReport, LeaveReportSuppliers, LeaveReportClerk, FeedBackSuppliers, FeedBackClerk, NotificationSupplier, NotificationClerk

# Register your models here.
class UserModel(UserAdmin):
    pass


admin.site.register(CustomUser, UserModel)

admin.site.register(AdminManager)
admin.site.register(Clerk)
admin.site.register(Coffee_types)
admin.site.register(Batch)
admin.site.register(Suppliers)
admin.site.register(Attendance)
admin.site.register(AttendanceReport)
admin.site.register(LeaveReportSuppliers)
admin.site.register(LeaveReportClerk)
admin.site.register(FeedBackSuppliers)
admin.site.register(FeedBackClerk)
admin.site.register(NotificationSupplier)
admin.site.register(NotificationClerk)
