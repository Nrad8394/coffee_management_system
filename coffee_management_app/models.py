from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver




class SeasonYearModel(models.Model):
    id = models.AutoField(primary_key=True)
    season_start_year = models.DateField()
    season_end_year = models.DateField()
    objects = models.Manager()



# Overriding the Default Django Auth User and adding One More Field (user_type)
class CustomUser(AbstractUser):
    user_type_data = ((1, "AdminManager"), (2, "Clerk"), (3, "Supplier"))
    user_type = models.CharField(default=1, choices=user_type_data, max_length=10)



class AdminManager(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(CustomUser, on_delete = models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


class Clerk(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(CustomUser, on_delete = models.CASCADE)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


class Coffee_types(models.Model):
    id = models.AutoField(primary_key=True)
    coffee_types_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    # def __str__(self):
	#     return self.coffee_types_name



class Batch(models.Model):
    id =models.AutoField(primary_key=True)
    batch_name = models.CharField(max_length=255)
    coffee_types_id = models.ForeignKey(Coffee_types, on_delete=models.CASCADE, default=1) #need to give defauult coffee_type
    clerk_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()



class Suppliers(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(CustomUser, on_delete = models.CASCADE)
    gender = models.CharField(max_length=50)
    profile_pic = models.FileField()
    address = models.TextField()
    coffee_types_id = models.ForeignKey(Coffee_types, on_delete=models.DO_NOTHING, default=1)
    season_year_id = models.ForeignKey(SeasonYearModel, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


class Attendance(models.Model):
    # Batch Attendance
    id = models.AutoField(primary_key=True)
    batch_id = models.ForeignKey(Batch, on_delete=models.DO_NOTHING)
    attendance_date = models.DateField()
    season_year_id = models.ForeignKey(SeasonYearModel, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


class AttendanceReport(models.Model):
    # Individual Supplier Attendance
    id = models.AutoField(primary_key=True)
    suppliers_id = models.ForeignKey(Suppliers, on_delete=models.DO_NOTHING)
    attendance_id = models.ForeignKey(Attendance, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


class LeaveReportSuppliers(models.Model):
    id = models.AutoField(primary_key=True)
    suppliers_id = models.ForeignKey(Suppliers, on_delete=models.CASCADE)
    leave_date = models.CharField(max_length=255)
    leave_message = models.TextField()
    leave_status = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


class LeaveReportClerk(models.Model):
    id = models.AutoField(primary_key=True)
    clerk_id = models.ForeignKey(Clerk, on_delete=models.CASCADE)
    leave_date = models.CharField(max_length=255)
    leave_message = models.TextField()
    leave_status = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


class FeedBackSuppliers(models.Model):
    id = models.AutoField(primary_key=True)
    suppliers_id = models.ForeignKey(Suppliers, on_delete=models.CASCADE)
    feedback = models.TextField()
    feedback_reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


class FeedBackClerk(models.Model):
    id = models.AutoField(primary_key=True)
    clerk_id = models.ForeignKey(Clerk, on_delete=models.CASCADE)
    feedback = models.TextField()
    feedback_reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()



class NotificationSupplier(models.Model):
    id = models.AutoField(primary_key=True)
    suppliers_id = models.ForeignKey(Suppliers, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


class NotificationClerk(models.Model):
    id = models.AutoField(primary_key=True)
    clerk_id = models.ForeignKey(Clerk, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


class SupplierResult(models.Model):
    id = models.AutoField(primary_key=True)
    suppliers_id = models.ForeignKey(Suppliers, on_delete=models.CASCADE)
    batch_id = models.ForeignKey(Batch, on_delete=models.CASCADE)
    batch_exam_marks = models.FloatField(default=0)
    batch_assignment_marks = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


#Creating Django Signals

# It's like trigger in database. It will run only when Data is Added in CustomUser model

@receiver(post_save, sender=CustomUser)
# Now Creating a Function which will automatically insert data in AdminManager, Clerk or Supplier
def create_user_profile(sender, instance, created, **kwargs):
    # if Created is true (Means Data Inserted)
    if created:
        # Check the user_type and insert the data in respective tables
        if instance.user_type == 1:
            AdminManager.objects.create(user=instance)
        if instance.user_type == 2:
            Clerk.objects.create(user=instance)
        if instance.user_type == 3:
            Suppliers.objects.create(user=instance, coffee_types_id=Coffee_types.objects.get(id=1), season_year_id=SeasonYearModel.objects.get(id=1), address="", profile_pic="", gender="")
    

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if instance.user_type == 1:
        instance.adminmanager.save()
    if instance.user_type == 2:
        instance.clerk.save()
    if instance.user_type == 3:
        instance.suppliers.save()
    


