from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.core.files.storage import FileSystemStorage #To upload Profile Picture
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
import json


from coffee_management_app.models import CustomUser, Clerk, Courses, Subjects, Suppliers, SessionYearModel, Attendance, AttendanceReport, LeaveReportClerk, FeedBackClerk, SupplierResult


def clerk_home(request):
    # Fetching All Suppliers under Clerk

    subjects = Subjects.objects.filter(clerk_id=request.user.id)
    course_id_list = []
    for batch in subjects:
        coffee_type = Courses.objects.get(id=batch.course_id.id)
        course_id_list.append(coffee_type.id)
    
    final_course = []
    # Removing Duplicate Coffee_type Id
    for course_id in course_id_list:
        if course_id not in final_course:
            final_course.append(course_id)
    
    students_count = Suppliers.objects.filter(course_id__in=final_course).count()
    subject_count = subjects.count()

    # Fetch All Attendance Count
    attendance_count = Attendance.objects.filter(subject_id__in=subjects).count()
    # Fetch All Approve Leave
    clerk = Clerk.objects.get(admin=request.user.id)
    leave_count = LeaveReportClerk.objects.filter(clerk_id=clerk.id, leave_status=1).count()

    #Fetch Attendance Data by Subjects
    subject_list = []
    attendance_list = []
    for batch in subjects:
        attendance_count1 = Attendance.objects.filter(subject_id=batch.id).count()
        subject_list.append(batch.subject_name)
        attendance_list.append(attendance_count1)

    students_attendance = Suppliers.objects.filter(course_id__in=final_course)
    student_list = []
    student_list_attendance_present = []
    student_list_attendance_absent = []
    for supplier in students_attendance:
        attendance_present_count = AttendanceReport.objects.filter(status=True, suppliers_id=supplier.id).count()
        attendance_absent_count = AttendanceReport.objects.filter(status=False, suppliers_id=supplier.id).count()
        student_list.append(supplier.admin.first_name+" "+ supplier.admin.last_name)
        student_list_attendance_present.append(attendance_present_count)
        student_list_attendance_absent.append(attendance_absent_count)

    context={
        "students_count": students_count,
        "attendance_count": attendance_count,
        "leave_count": leave_count,
        "subject_count": subject_count,
        "subject_list": subject_list,
        "attendance_list": attendance_list,
        "student_list": student_list,
        "attendance_present_list": student_list_attendance_present,
        "attendance_absent_list": student_list_attendance_absent
    }
    return render(request, "clerk_template/staff_home_template.html", context)



def clerk_take_attendance(request):
    subjects = Subjects.objects.filter(clerk_id=request.user.id)
    session_years = SessionYearModel.objects.all()
    context = {
        "subjects": subjects,
        "session_years": session_years
    }
    return render(request, "clerk_template/take_attendance_template.html", context)


def clerk_apply_leave(request):
    staff_obj = Clerk.objects.get(admin=request.user.id)
    leave_data = LeaveReportClerk.objects.filter(clerk_id=staff_obj)
    context = {
        "leave_data": leave_data
    }
    return render(request, "clerk_template/staff_apply_leave_template.html", context)


def clerk_apply_leave_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('clerk_apply_leave')
    else:
        leave_date = request.POST.get('leave_date')
        leave_message = request.POST.get('leave_message')

        staff_obj = Clerk.objects.get(admin=request.user.id)
        try:
            leave_report = LeaveReportClerk(clerk_id=staff_obj, leave_date=leave_date, leave_message=leave_message, leave_status=0)
            leave_report.save()
            messages.success(request, "Applied for Leave.")
            return redirect('clerk_apply_leave')
        except:
            messages.error(request, "Failed to Apply Leave")
            return redirect('clerk_apply_leave')


def clerk_feedback(request):
    staff_obj = Clerk.objects.get(admin=request.user.id)
    feedback_data = FeedBackClerk.objects.filter(clerk_id=staff_obj)
    context = {
        "feedback_data":feedback_data
    }
    return render(request, "clerk_template/staff_feedback_template.html", context)


def clerk_feedback_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method.")
        return redirect('clerk_feedback')
    else:
        feedback = request.POST.get('feedback_message')
        staff_obj = Clerk.objects.get(admin=request.user.id)

        try:
            add_feedback = FeedBackClerk(clerk_id=staff_obj, feedback=feedback, feedback_reply="")
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
    subject_id = request.POST.get("batch")
    session_year = request.POST.get("session_year")

    # Suppliers enroll to Coffee_type, Coffee_type has Subjects
    # Getting all data from batch model based on subject_id
    subject_model = Subjects.objects.get(id=subject_id)

    session_model = SessionYearModel.objects.get(id=session_year)

    students = Suppliers.objects.filter(course_id=subject_model.course_id, session_year_id=session_model)

    # Only Passing Supplier Id and Supplier Name Only
    list_data = []

    for supplier in students:
        data_small={"id":supplier.admin.id, "name":supplier.admin.first_name+" "+supplier.admin.last_name}
        list_data.append(data_small)

    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)




@csrf_exempt
def save_attendance_data(request):
    # Get Values from Staf Take Attendance form via AJAX (JavaScript)
    # Use getlist to access HTML Array/List Input Data
    student_ids = request.POST.get("student_ids")
    subject_id = request.POST.get("subject_id")
    attendance_date = request.POST.get("attendance_date")
    session_year_id = request.POST.get("session_year_id")

    subject_model = Subjects.objects.get(id=subject_id)
    session_year_model = SessionYearModel.objects.get(id=session_year_id)

    json_student = json.loads(student_ids)
    # print(dict_student[0]['id'])

    # print(student_ids)
    try:
        # First Attendance Data is Saved on Attendance Model
        attendance = Attendance(subject_id=subject_model, attendance_date=attendance_date, session_year_id=session_year_model)
        attendance.save()

        for stud in json_student:
            # Attendance of Individual Supplier saved on AttendanceReport Model
            supplier = Suppliers.objects.get(admin=stud['id'])
            attendance_report = AttendanceReport(suppliers_id=supplier, attendance_id=attendance, status=stud['status'])
            attendance_report.save()
        return HttpResponse("OK")
    except:
        return HttpResponse("Error")




def clerk_update_attendance(request):
    subjects = Subjects.objects.filter(clerk_id=request.user.id)
    session_years = SessionYearModel.objects.all()
    context = {
        "subjects": subjects,
        "session_years": session_years
    }
    return render(request, "clerk_template/update_attendance_template.html", context)

@csrf_exempt
def get_attendance_dates(request):
    

    # Getting Values from Ajax POST 'Fetch Supplier'
    subject_id = request.POST.get("batch")
    session_year = request.POST.get("session_year_id")

    # Suppliers enroll to Coffee_type, Coffee_type has Subjects
    # Getting all data from batch model based on subject_id
    subject_model = Subjects.objects.get(id=subject_id)

    session_model = SessionYearModel.objects.get(id=session_year)

    # students = Suppliers.objects.filter(course_id=subject_model.course_id, session_year_id=session_model)
    attendance = Attendance.objects.filter(subject_id=subject_model, session_year_id=session_model)

    # Only Passing Supplier Id and Supplier Name Only
    list_data = []

    for attendance_single in attendance:
        data_small={"id":attendance_single.id, "attendance_date":str(attendance_single.attendance_date), "session_year_id":attendance_single.session_year_id.id}
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
        data_small={"id":supplier.suppliers_id.admin.id, "name":supplier.suppliers_id.admin.first_name+" "+supplier.suppliers_id.admin.last_name, "status":supplier.status}
        list_data.append(data_small)

    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)


@csrf_exempt
def update_attendance_data(request):
    student_ids = request.POST.get("student_ids")

    attendance_date = request.POST.get("attendance_date")
    attendance = Attendance.objects.get(id=attendance_date)

    json_student = json.loads(student_ids)

    try:
        
        for stud in json_student:
            # Attendance of Individual Supplier saved on AttendanceReport Model
            supplier = Suppliers.objects.get(admin=stud['id'])

            attendance_report = AttendanceReport.objects.get(suppliers_id=supplier, attendance_id=attendance)
            attendance_report.status=stud['status']

            attendance_report.save()
        return HttpResponse("OK")
    except:
        return HttpResponse("Error")


def clerk_profile(request):
    user = CustomUser.objects.get(id=request.user.id)
    clerk = Clerk.objects.get(admin=user)

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

            clerk = Clerk.objects.get(admin=customuser.id)
            clerk.address = address
            clerk.save()

            messages.success(request, "Profile Updated Successfully")
            return redirect('clerk_profile')
        except:
            messages.error(request, "Failed to Update Profile")
            return redirect('clerk_profile')



def clerk_add_result(request):
    subjects = Subjects.objects.filter(clerk_id=request.user.id)
    session_years = SessionYearModel.objects.all()
    context = {
        "subjects": subjects,
        "session_years": session_years,
    }
    return render(request, "clerk_template/add_result_template.html", context)


def clerk_add_result_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('clerk_add_result')
    else:
        student_admin_id = request.POST.get('student_list')
        assignment_marks = request.POST.get('assignment_marks')
        exam_marks = request.POST.get('exam_marks')
        subject_id = request.POST.get('batch')

        student_obj = Suppliers.objects.get(admin=student_admin_id)
        subject_obj = Subjects.objects.get(id=subject_id)

        try:
            # Check if Suppliers Result Already Exists or not
            check_exist = SupplierResult.objects.filter(subject_id=subject_obj, suppliers_id=student_obj).exists()
            if check_exist:
                result = SupplierResult.objects.get(subject_id=subject_obj, suppliers_id=student_obj)
                result.subject_assignment_marks = assignment_marks
                result.subject_exam_marks = exam_marks
                result.save()
                messages.success(request, "Result Updated Successfully!")
                return redirect('clerk_add_result')
            else:
                result = SupplierResult(suppliers_id=student_obj, subject_id=subject_obj, subject_exam_marks=exam_marks, subject_assignment_marks=assignment_marks)
                result.save()
                messages.success(request, "Result Added Successfully!")
                return redirect('clerk_add_result')
        except:
            messages.error(request, "Failed to Add Result!")
            return redirect('clerk_add_result')
