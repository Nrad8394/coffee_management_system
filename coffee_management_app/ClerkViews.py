from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.core.files.storage import FileSystemStorage #To upload Profile Picture
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
import json


from coffee_management_app.models import CustomUser, Clerk, Coffee_types, Batch, Suppliers, SeasonYearModel, Attendance, AttendanceReport, LeaveReportClerk, FeedBackClerk, SupplierCoffeedata


def clerk_home(request):
    # Fetching All Suppliers under Clerk

    batchs = Batch.objects.filter(clerk_id=request.user.id)
    coffee_types_id_list = []
    for batch in batchs:
        coffee_type = Coffee_types.objects.get(id=batch.coffee_types_id.id)
        coffee_types_id_list.append(coffee_type.id)
    
    final_coffee_types = []
    # Removing Duplicate Coffee_type Id
    for coffee_types_id in coffee_types_id_list:
        if coffee_types_id not in final_coffee_types:
            final_coffee_types.append(coffee_types_id)
    
    suppliers_count = Suppliers.objects.filter(coffee_types_id__in=final_coffee_types).count()
    batch_count = batchs.count()

    # Fetch All Attendance Count
    attendance_count = Attendance.objects.filter(batch_id__in=batchs).count()
    # Fetch All Approve Leave
    clerk = Clerk.objects.get(user=request.user.id)
    leave_count = LeaveReportClerk.objects.filter(clerk_id=clerk.id, leave_status=1).count()

    #Fetch Attendance Data by Batch
    batch_list = []
    attendance_list = []
    for batch in batchs:
        attendance_count1 = Attendance.objects.filter(batch_id=batch.id).count()
        batch_list.append(batch.batch_name)
        attendance_list.append(attendance_count1)

    suppliers_attendance = Suppliers.objects.filter(coffee_types_id__in=final_coffee_types)
    supplier_list = []
    supplier_list_attendance_present = []
    supplier_list_attendance_absent = []
    for supplier in suppliers_attendance:
        attendance_present_count = AttendanceReport.objects.filter(status=True, suppliers_id=supplier.id).count()
        attendance_absent_count = AttendanceReport.objects.filter(status=False, suppliers_id=supplier.id).count()
        supplier_list.append(supplier.user.first_name+" "+ supplier.user.last_name)
        supplier_list_attendance_present.append(attendance_present_count)
        supplier_list_attendance_absent.append(attendance_absent_count)

    context={
        "suppliers_count": suppliers_count,
        "attendance_count": attendance_count,
        "leave_count": leave_count,
        "batch_count": batch_count,
        "batch_list": batch_list,
        "attendance_list": attendance_list,
        "supplier_list": supplier_list,
        "attendance_present_list": supplier_list_attendance_present,
        "attendance_absent_list": supplier_list_attendance_absent
    }
    return render(request, "clerk_template/clerk_home_template.html", context)



def clerk_take_attendance(request):
    batchs = Batch.objects.filter(clerk_id=request.user.id)
    season_years = SeasonYearModel.objects.all()
    context = {
        "batchs": batchs,
        "season_years": season_years
    }
    return render(request, "clerk_template/take_attendance_template.html", context)


def clerk_apply_leave(request):
    clerk_obj = Clerk.objects.get(user=request.user.id)
    leave_data = LeaveReportClerk.objects.filter(clerk_id=clerk_obj)
    context = {
        "leave_data": leave_data
    }
    return render(request, "clerk_template/clerk_apply_leave_template.html", context)


def clerk_apply_leave_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('clerk_apply_leave')
    else:
        leave_date = request.POST.get('leave_date')
        leave_message = request.POST.get('leave_message')

        clerk_obj = Clerk.objects.get(user=request.user.id)
        try:
            leave_report = LeaveReportClerk(clerk_id=clerk_obj, leave_date=leave_date, leave_message=leave_message, leave_status=0)
            leave_report.save()
            messages.success(request, "Applied for Leave.")
            return redirect('clerk_apply_leave')
        except:
            messages.error(request, "Failed to Apply Leave")
            return redirect('clerk_apply_leave')


def clerk_feedback(request):
    clerk_obj = Clerk.objects.get(user=request.user.id)
    feedback_data = FeedBackClerk.objects.filter(clerk_id=clerk_obj)
    context = {
        "feedback_data":feedback_data
    }
    return render(request, "clerk_template/clerk_feedback_template.html", context)


def clerk_feedback_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method.")
        return redirect('clerk_feedback')
    else:
        feedback = request.POST.get('feedback_message')
        clerk_obj = Clerk.objects.get(user=request.user.id)

        try:
            add_feedback = FeedBackClerk(clerk_id=clerk_obj, feedback=feedback, feedback_reply="")
            add_feedback.save()
            messages.success(request, "Feedback Sent.")
            return redirect('clerk_feedback')
        except:
            messages.error(request, "Failed to Send Feedback.")
            return redirect('clerk_feedback')


# WE don't need csrf_token when using Ajax
@csrf_exempt
def get_suppliers(request):
    # Getting Values from Ajax POST 'Fetch Supplier'
    batch_id = request.POST.get("batch")
    season_year = request.POST.get("season_year")

    # Suppliers enroll to Coffee_type, Coffee_type has Batch
    # Getting all data from batch model based on batch_id
    batch_model = Batch.objects.get(id=batch_id)

    season_model = SeasonYearModel.objects.get(id=season_year)

    suppliers = Suppliers.objects.filter(coffee_types_id=batch_model.coffee_types_id, season_year_id=season_model)

    # Only Passing Supplier Id and Supplier Name Only
    list_data = []

    for supplier in suppliers:
        data_small={"id":supplier.user.id, "name":supplier.user.first_name+" "+supplier.user.last_name}
        list_data.append(data_small)

    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)




@csrf_exempt
def save_attendance_data(request):
    # Get Values from Staf Take Attendance form via AJAX (JavaScript)
    # Use getlist to access HTML Array/List Input Data
    supplier_ids = request.POST.get("supplier_ids")
    batch_id = request.POST.get("batch_id")
    attendance_date = request.POST.get("attendance_date")
    season_year_id = request.POST.get("season_year_id")

    batch_model = Batch.objects.get(id=batch_id)
    season_year_model = SeasonYearModel.objects.get(id=season_year_id)

    json_supplier = json.loads(supplier_ids)
    # print(dict_supplier[0]['id'])

    # print(supplier_ids)
    try:
        # First Attendance Data is Saved on Attendance Model
        attendance = Attendance(batch_id=batch_model, attendance_date=attendance_date, season_year_id=season_year_model)
        attendance.save()

        for stud in json_supplier:
            # Attendance of Individual Supplier saved on AttendanceReport Model
            supplier = Suppliers.objects.get(user=stud['id'])
            attendance_report = AttendanceReport(suppliers_id=supplier, attendance_id=attendance, status=stud['status'])
            attendance_report.save()
        return HttpResponse("OK")
    except:
        return HttpResponse("Error")




def clerk_update_attendance(request):
    batchs = Batch.objects.filter(clerk_id=request.user.id)
    season_years = SeasonYearModel.objects.all()
    context = {
        "batchs": batchs,
        "season_years": season_years
    }
    return render(request, "clerk_template/update_attendance_template.html", context)

@csrf_exempt
def get_attendance_dates(request):
    

    # Getting Values from Ajax POST 'Fetch Supplier'
    batch_id = request.POST.get("batch")
    season_year = request.POST.get("season_year_id")

    # Suppliers enroll to Coffee_type, Coffee_type has Batch
    # Getting all data from batch model based on batch_id
    batch_model = Batch.objects.get(id=batch_id)

    season_model = SeasonYearModel.objects.get(id=season_year)

    # suppliers = Suppliers.objects.filter(coffee_types_id=batch_model.coffee_types_id, season_year_id=season_model)
    attendance = Attendance.objects.filter(batch_id=batch_model, season_year_id=season_model)

    # Only Passing Supplier Id and Supplier Name Only
    list_data = []

    for attendance_single in attendance:
        data_small={"id":attendance_single.id, "attendance_date":str(attendance_single.attendance_date), "season_year_id":attendance_single.season_year_id.id}
        list_data.append(data_small)

    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)


@csrf_exempt
def get_attendance_supplier(request):
    # Getting Values from Ajax POST 'Fetch Supplier'
    attendance_date = request.POST.get('attendance_date')
    attendance = Attendance.objects.get(id=attendance_date)

    attendance_data = AttendanceReport.objects.filter(attendance_id=attendance)
    # Only Passing Supplier Id and Supplier Name Only
    list_data = []

    for supplier in attendance_data:
        data_small={"id":supplier.suppliers_id.user.id, "name":supplier.suppliers_id.user.first_name+" "+supplier.suppliers_id.user.last_name, "status":supplier.status}
        list_data.append(data_small)

    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)


@csrf_exempt
def update_attendance_data(request):
    supplier_ids = request.POST.get("supplier_ids")

    attendance_date = request.POST.get("attendance_date")
    attendance = Attendance.objects.get(id=attendance_date)

    json_supplier = json.loads(supplier_ids)

    try:
        
        for stud in json_supplier:
            # Attendance of Individual Supplier saved on AttendanceReport Model
            supplier = Suppliers.objects.get(user=stud['id'])

            attendance_report = AttendanceReport.objects.get(suppliers_id=supplier, attendance_id=attendance)
            attendance_report.status=stud['status']

            attendance_report.save()
        return HttpResponse("OK")
    except:
        return HttpResponse("Error")


def clerk_profile(request):
    user = CustomUser.objects.get(id=request.user.id)
    clerk = Clerk.objects.get(user=user)

    context={
        "user": user,
        "clerk": clerk
    }
    return render(request, 'clerk_template/clerk_profile.html', context)


def clerk_profile_update(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('clerk_profile')
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

            clerk = Clerk.objects.get(user=customuser.id)
            clerk.address = address
            clerk.save()

            messages.success(request, "Profile Updated Successfully")
            return redirect('clerk_profile')
        except:
            messages.error(request, "Failed to Update Profile")
            return redirect('clerk_profile')



def clerk_add_coffee_data(request):
    batchs = Batch.objects.filter(clerk_id=request.user.id)
    season_years = SeasonYearModel.objects.all()
    context = {
        "batchs": batchs,
        "season_years": season_years,
    }
    return render(request, "clerk_template/add_coffee_data_template.html", context)


def clerk_add_coffee_data_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('clerk_add_coffee_data')
    else: 
        supplier_admin_id = request.POST.get('supplier_list')
        assignment_marks = request.POST.get('assignment_marks')
        coffee_amount = request.POST.get('coffee_amount')
        batch_id = request.POST.get('batch')

        supplier_obj = Suppliers.objects.get(user=supplier_admin_id)
        batch_obj = Batch.objects.get(id=batch_id)

        try:
            # Check if Suppliers Coffee data Already Exists or not
            check_exist = SupplierCoffeedata.objects.filter(batch_id=batch_obj, suppliers_id=supplier_obj).exists()
            if check_exist:
                result = SupplierCoffeedata.objects.get(batch_id=batch_obj, suppliers_id=supplier_obj)
                result.coffee_grade = assignment_marks
                result.coffee_amount = coffee_amount 
                result.save()
                messages.success(request, "Coffee data Updated Successfully!")
                return redirect('clerk_add_coffee_data')
            else:
                result = SupplierCoffeedata(suppliers_id=supplier_obj, batch_id=batch_obj, coffee_amount=coffee_amount, coffee_grade=assignment_marks)
                result.save()
                messages.success(request, "Coffee data Added Successfully!")
                return redirect('clerk_add_coffee_data')
        except:
            messages.error(request, "Failed to Add Coffee data!")
            return redirect('clerk_add_coffee_data')
