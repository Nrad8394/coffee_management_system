from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.core.files.storage import FileSystemStorage #To upload Profile Picture
from django.urls import reverse
import datetime # To Parse input DateTime into Python Date Time Object

from coffee_management_app.models import CustomUser, Clerk, Coffee_types, Batch, Suppliers, Attendance, AttendanceReport, LeaveReportSuppliers, FeedBackSuppliers, SupplierResult


def supplier_home(request):
    supplier_obj = Suppliers.objects.get(user=request.user.id)
    total_attendance = AttendanceReport.objects.filter(suppliers_id=supplier_obj).count()
    attendance_present = AttendanceReport.objects.filter(suppliers_id=supplier_obj, status=True).count()
    attendance_absent = AttendanceReport.objects.filter(suppliers_id=supplier_obj, status=False).count()

    coffee_types_obj = Coffee_types.objects.get(id=supplier_obj.coffee_types_id.id)
    total_batchs = Batch.objects.filter(coffee_types_id=coffee_types_obj).count()

    batch_name = []
    data_present = []
    data_absent = []
    batch_data = Batch.objects.filter(coffee_types_id=supplier_obj.coffee_types_id)
    for batch in batch_data:
        attendance = Attendance.objects.filter(batch_id=batch.id)
        attendance_present_count = AttendanceReport.objects.filter(attendance_id__in=attendance, status=True, suppliers_id=supplier_obj.id).count()
        attendance_absent_count = AttendanceReport.objects.filter(attendance_id__in=attendance, status=False, suppliers_id=supplier_obj.id).count()
        batch_name.append(batch.batch_name)
        data_present.append(attendance_present_count)
        data_absent.append(attendance_absent_count)
    
    context={
        "total_attendance": total_attendance,
        "attendance_present": attendance_present,
        "attendance_absent": attendance_absent,
        "total_batchs": total_batchs,
        "batch_name": batch_name,
        "data_present": data_present,
        "data_absent": data_absent
    }
    return render(request, "supplier_template/supplier_home_template.html", context)


def supplier_view_attendance(request):
    supplier = Suppliers.objects.get(user=request.user.id) # Getting Logged in Supplier Data
    coffee_type = supplier.coffee_types_id # Getting Coffee_type Enrolled of LoggedIn Supplier
    # coffee_type = Coffee_types.objects.get(id=supplier.coffee_types_id.id) # Getting Coffee_type Enrolled of LoggedIn Supplier
    batchs = Batch.objects.filter(coffee_types_id=coffee_type) # Getting the Batch of Coffee_type Enrolled
    context = {
        "batchs": batchs
    }
    return render(request, "supplier_template/supplier_view_attendance.html", context)


def supplier_view_attendance_post(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('supplier_view_attendance')
    else:
        # Getting all the Input Data
        batch_id = request.POST.get('batch')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        # Parsing the date data into Python object
        start_date_parse = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_parse = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()

        # Getting all the Batch Data based on Selected Batch
        batch_obj = Batch.objects.get(id=batch_id)
        # Getting Logged In User Data
        user_obj = CustomUser.objects.get(id=request.user.id)
        # Getting Supplier Data Based on Logged in Data
        stud_obj = Suppliers.objects.get(user=user_obj)

        # Now Accessing Attendance Data based on the Range of Date Selected and Batch Selected
        attendance = Attendance.objects.filter(attendance_date__range=(start_date_parse, end_date_parse), batch_id=batch_obj)
        # Getting Attendance Report based on the attendance details obtained above
        attendance_reports = AttendanceReport.objects.filter(attendance_id__in=attendance, suppliers_id=stud_obj)

        # for attendance_report in attendance_reports:
        #     print("Date: "+ str(attendance_report.attendance_id.attendance_date), "Status: "+ str(attendance_report.status))

        # messages.success(request, "Attendacne View Success")

        context = {
            "batch_obj": batch_obj,
            "attendance_reports": attendance_reports
        }

        return render(request, 'supplier_template/supplier_attendance_data.html', context)
       

def supplier_apply_leave(request):
    supplier_obj = Suppliers.objects.get(user=request.user.id)
    leave_data = LeaveReportSuppliers.objects.filter(suppliers_id=supplier_obj)
    context = {
        "leave_data": leave_data
    }
    return render(request, 'supplier_template/supplier_apply_leave.html', context)


def supplier_apply_leave_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('supplier_apply_leave')
    else:
        leave_date = request.POST.get('leave_date')
        leave_message = request.POST.get('leave_message')

        supplier_obj = Suppliers.objects.get(user=request.user.id)
        try:
            leave_report = LeaveReportSuppliers(suppliers_id=supplier_obj, leave_date=leave_date, leave_message=leave_message, leave_status=0)
            leave_report.save()
            messages.success(request, "Applied for Leave.")
            return redirect('supplier_apply_leave')
        except:
            messages.error(request, "Failed to Apply Leave")
            return redirect('supplier_apply_leave')


def supplier_feedback(request):
    supplier_obj = Suppliers.objects.get(user=request.user.id)
    feedback_data = FeedBackSuppliers.objects.filter(suppliers_id=supplier_obj)
    context = {
        "feedback_data": feedback_data
    }
    return render(request, 'supplier_template/supplier_feedback.html', context)


def supplier_feedback_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method.")
        return redirect('supplier_feedback')
    else:
        feedback = request.POST.get('feedback_message')
        supplier_obj = Suppliers.objects.get(user=request.user.id)

        try:
            add_feedback = FeedBackSuppliers(suppliers_id=supplier_obj, feedback=feedback, feedback_reply="")
            add_feedback.save()
            messages.success(request, "Feedback Sent.")
            return redirect('supplier_feedback')
        except:
            messages.error(request, "Failed to Send Feedback.")
            return redirect('supplier_feedback')


def supplier_profile(request):
    user = CustomUser.objects.get(id=request.user.id)
    supplier = Suppliers.objects.get(user=user)

    context={
        "user": user,
        "supplier": supplier
    }
    return render(request, 'supplier_template/supplier_profile.html', context)


def supplier_profile_update(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('supplier_profile')
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        address = request.POST.get('address')

        try:
            customuser = CustomUser.objects.get(id=request.user.id)
            customuser.first_name = first_name
            customuser.last_name = last_name
            if password != None and password != "":
                customuser.set_password(password)
            customuser.save()

            supplier = Suppliers.objects.get(user=customuser.id)
            supplier.address = address
            supplier.save()
            
            messages.success(request, "Profile Updated Successfully")
            return redirect('supplier_profile')
        except:
            messages.error(request, "Failed to Update Profile")
            return redirect('supplier_profile')


def supplier_view_result(request):
    supplier = Suppliers.objects.get(user=request.user.id)
    supplier_result = SupplierResult.objects.filter(suppliers_id=supplier.id)
    context = {
        "supplier_result": supplier_result,
    }
    return render(request, "supplier_template/supplier_view_result.html", context)





