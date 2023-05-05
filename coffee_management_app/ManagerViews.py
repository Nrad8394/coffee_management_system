from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.core.files.storage import FileSystemStorage #To upload Profile Picture
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
import json

from .models import CustomUser, Clerk, Courses, Subjects, Suppliers, SessionYearModel, FeedBackSuppliers, FeedBackClerk, LeaveReportSuppliers, LeaveReportClerk, Attendance, AttendanceReport
from .forms import AddStudentForm, EditStudentForm


def admin_home(request):
    all_student_count = Suppliers.objects.all().count()
    subject_count = Subjects.objects.all().count()
    course_count = Courses.objects.all().count()
    staff_count = Clerk.objects.all().count()

    # Total Subjects and students in Each Coffee_type
    course_all = Courses.objects.all()
    course_name_list = []
    subject_count_list = []
    student_count_list_in_course = []

    for coffee_type in course_all:
        subjects = Subjects.objects.filter(course_id=coffee_type.id).count()
        students = Suppliers.objects.filter(course_id=coffee_type.id).count()
        course_name_list.append(coffee_type.course_name)
        subject_count_list.append(subjects)
        student_count_list_in_course.append(students)
    
    subject_all = Subjects.objects.all()
    subject_list = []
    student_count_list_in_subject = []
    for batch in subject_all:
        coffee_type = Courses.objects.get(id=batch.course_id.id)
        student_count = Suppliers.objects.filter(course_id=coffee_type.id).count()
        subject_list.append(batch.subject_name)
        student_count_list_in_subject.append(student_count)
    
    # For Saffs
    staff_attendance_present_list=[]
    staff_attendance_leave_list=[]
    staff_name_list=[]

    staffs = Clerk.objects.all()
    for clerk in staffs:
        subject_ids = Subjects.objects.filter(clerk_id=clerk.admin.id)
        attendance = Attendance.objects.filter(subject_id__in=subject_ids).count()
        leaves = LeaveReportClerk.objects.filter(clerk_id=clerk.id, leave_status=1).count()
        staff_attendance_present_list.append(attendance)
        staff_attendance_leave_list.append(leaves)
        staff_name_list.append(clerk.admin.first_name)

    # For Suppliers
    student_attendance_present_list=[]
    student_attendance_leave_list=[]
    student_name_list=[]

    students = Suppliers.objects.all()
    for supplier in students:
        attendance = AttendanceReport.objects.filter(suppliers_id=supplier.id, status=True).count()
        absent = AttendanceReport.objects.filter(suppliers_id=supplier.id, status=False).count()
        leaves = LeaveReportSuppliers.objects.filter(suppliers_id=supplier.id, leave_status=1).count()
        student_attendance_present_list.append(attendance)
        student_attendance_leave_list.append(leaves+absent)
        student_name_list.append(supplier.admin.first_name)


    context={
        "all_student_count": all_student_count,
        "subject_count": subject_count,
        "course_count": course_count,
        "staff_count": staff_count,
        "course_name_list": course_name_list,
        "subject_count_list": subject_count_list,
        "student_count_list_in_course": student_count_list_in_course,
        "subject_list": subject_list,
        "student_count_list_in_subject": student_count_list_in_subject,
        "staff_attendance_present_list": staff_attendance_present_list,
        "staff_attendance_leave_list": staff_attendance_leave_list,
        "staff_name_list": staff_name_list,
        "student_attendance_present_list": student_attendance_present_list,
        "student_attendance_leave_list": student_attendance_leave_list,
        "student_name_list": student_name_list,
    }
    return render(request, "admin_template/home_content.html", context)


def add_clerk(request):
    return render(request, "admin_template/add_staff_template.html")


def add_clerk_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method ")
        return redirect('add_clerk')
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        address = request.POST.get('address')

        try:
            user = CustomUser.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name, user_type=2)
            user.staffs.address = address
            user.save()
            messages.success(request, "Clerk Added Successfully!")
            return redirect('add_clerk')
        except:
            messages.error(request, "Failed to Add Clerk!")
            return redirect('add_clerk')



def manage_clerk(request):
    staffs = Clerk.objects.all()
    context = {
        "staffs": staffs
    }
    return render(request, "admin_template/manage_staff_template.html", context)


def edit_clerk(request, clerk_id):
    clerk = Clerk.objects.get(admin=clerk_id)

    context = {
        "clerk": clerk,
        "id": clerk_id
    }
    return render(request, "admin_template/edit_staff_template.html", context)


def edit_clerk_save(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        clerk_id = request.POST.get('clerk_id')
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        address = request.POST.get('address')

        try:
            # INSERTING into Customuser Model
            user = CustomUser.objects.get(id=clerk_id)
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.username = username
            user.save()
            
            # INSERTING into Clerk Model
            staff_model = Clerk.objects.get(admin=clerk_id)
            staff_model.address = address
            staff_model.save()

            messages.success(request, "Clerk Updated Successfully.")
            return redirect('/edit_clerk/'+clerk_id)

        except:
            messages.error(request, "Failed to Update Clerk.")
            return redirect('/edit_clerk/'+clerk_id)



def delete_clerk(request, clerk_id):
    clerk = Clerk.objects.get(admin=clerk_id)
    try:
        clerk.delete()
        messages.success(request, "Clerk Deleted Successfully.")
        return redirect('manage_clerk')
    except:
        messages.error(request, "Failed to Delete Clerk.")
        return redirect('manage_clerk')




def add_course(request):
    return render(request, "admin_template/add_course_template.html")


def add_course_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('add_course')
    else:
        coffee_type = request.POST.get('coffee_type')
        try:
            course_model = Courses(course_name=coffee_type)
            course_model.save()
            messages.success(request, "Coffee_type Added Successfully!")
            return redirect('add_course')
        except:
            messages.error(request, "Failed to Add Coffee_type!")
            return redirect('add_course')


def manage_course(request):
    courses = Courses.objects.all()
    context = {
        "courses": courses
    }
    return render(request, 'admin_template/manage_course_template.html', context)


def edit_course(request, course_id):
    coffee_type = Courses.objects.get(id=course_id)
    context = {
        "coffee_type": coffee_type,
        "id": course_id
    }
    return render(request, 'admin_template/edit_course_template.html', context)


def edit_course_save(request):
    if request.method != "POST":
        HttpResponse("Invalid Method")
    else:
        course_id = request.POST.get('course_id')
        course_name = request.POST.get('coffee_type')

        try:
            coffee_type = Courses.objects.get(id=course_id)
            coffee_type.course_name = course_name
            coffee_type.save()

            messages.success(request, "Coffee_type Updated Successfully.")
            return redirect('/edit_course/'+course_id)

        except:
            messages.error(request, "Failed to Update Coffee_type.")
            return redirect('/edit_course/'+course_id)


def delete_course(request, course_id):
    coffee_type = Courses.objects.get(id=course_id)
    try:
        coffee_type.delete()
        messages.success(request, "Coffee_type Deleted Successfully.")
        return redirect('manage_course')
    except:
        messages.error(request, "Failed to Delete Coffee_type.")
        return redirect('manage_course')


def manage_session(request):
    session_years = SessionYearModel.objects.all()
    context = {
        "session_years": session_years
    }
    return render(request, "admin_template/manage_session_template.html", context)


def add_session(request):
    return render(request, "admin_template/add_session_template.html")


def add_session_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('add_course')
    else:
        session_start_year = request.POST.get('session_start_year')
        session_end_year = request.POST.get('session_end_year')

        try:
            sessionyear = SessionYearModel(session_start_year=session_start_year, session_end_year=session_end_year)
            sessionyear.save()
            messages.success(request, "Season Year added Successfully!")
            return redirect("add_session")
        except:
            messages.error(request, "Failed to Add Season Year")
            return redirect("add_session")


def edit_session(request, session_id):
    session_year = SessionYearModel.objects.get(id=session_id)
    context = {
        "session_year": session_year
    }
    return render(request, "admin_template/edit_session_template.html", context)


def edit_session_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('manage_session')
    else:
        session_id = request.POST.get('session_id')
        session_start_year = request.POST.get('session_start_year')
        session_end_year = request.POST.get('session_end_year')

        try:
            session_year = SessionYearModel.objects.get(id=session_id)
            session_year.session_start_year = session_start_year
            session_year.session_end_year = session_end_year
            session_year.save()

            messages.success(request, "Season Year Updated Successfully.")
            return redirect('/edit_session/'+session_id)
        except:
            messages.error(request, "Failed to Update Season Year.")
            return redirect('/edit_session/'+session_id)


def delete_session(request, session_id):
    session = SessionYearModel.objects.get(id=session_id)
    try:
        session.delete()
        messages.success(request, "Season Deleted Successfully.")
        return redirect('manage_session')
    except:
        messages.error(request, "Failed to Delete Season.")
        return redirect('manage_session')


def add_suppliers(request):
    form = AddStudentForm()
    context = {
        "form": form
    }
    return render(request, 'admin_template/add_student_template.html', context)




def add_suppliers_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('add_suppliers')
    else:
        form = AddStudentForm(request.POST, request.FILES)

        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            address = form.cleaned_data['address']
            session_year_id = form.cleaned_data['session_year_id']
            course_id = form.cleaned_data['course_id']
            gender = form.cleaned_data['gender']

            # Getting Profile Pic first
            # First Check whether the file is selected or not
            # Upload only if file is selected
            if len(request.FILES) != 0:
                profile_pic = request.FILES['profile_pic']
                fs = FileSystemStorage()
                filename = fs.save(profile_pic.name, profile_pic)
                profile_pic_url = fs.url(filename)
            else:
                profile_pic_url = None


            try:
                user = CustomUser.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name, user_type=3)
                user.students.address = address

                course_obj = Courses.objects.get(id=course_id)
                user.students.course_id = course_obj

                session_year_obj = SessionYearModel.objects.get(id=session_year_id)
                user.students.session_year_id = session_year_obj

                user.students.gender = gender
                # user.students.profile_pic = profile_pic_url
                user.save()
                messages.success(request, "Supplier Added Successfully!")
                return redirect('add_suppliers')
            except:
                messages.error(request, "Failed to Add Supplier!")
                return redirect('add_suppliers')
        else:
            return redirect('add_suppliers')


def manage_suppliers(request):
    students = Suppliers.objects.all()
    context = {
        "students": students
    }
    return render(request, 'admin_template/manage_student_template.html', context)


def edit_suppliers(request, suppliers_id):
    # Adding Supplier ID into Season Variable
    request.session['suppliers_id'] = suppliers_id

    supplier = Suppliers.objects.get(admin=suppliers_id)
    form = EditStudentForm()
    # Filling the form with Data from Database
    form.fields['email'].initial = supplier.admin.email
    form.fields['username'].initial = supplier.admin.username
    form.fields['first_name'].initial = supplier.admin.first_name
    form.fields['last_name'].initial = supplier.admin.last_name
    form.fields['address'].initial = supplier.address
    form.fields['course_id'].initial = supplier.course_id.id
    form.fields['gender'].initial = supplier.gender
    form.fields['session_year_id'].initial = supplier.session_year_id.id

    context = {
        "id": suppliers_id,
        "username": supplier.admin.username,
        "form": form
    }
    return render(request, "admin_template/edit_student_template.html", context)


def edit_suppliers_save(request):
    if request.method != "POST":
        return HttpResponse("Invalid Method!")
    else:
        suppliers_id = request.session.get('suppliers_id')
        if suppliers_id == None:
            return redirect('/manage_suppliers')

        form = EditStudentForm(request.POST, request.FILES)
        if form.is_valid():
            email = form.cleaned_data['email']
            username = form.cleaned_data['username']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            address = form.cleaned_data['address']
            course_id = form.cleaned_data['course_id']
            gender = form.cleaned_data['gender']
            session_year_id = form.cleaned_data['session_year_id']

            # Getting Profile Pic first
            # First Check whether the file is selected or not
            # Upload only if file is selected
            if len(request.FILES) != 0:
                profile_pic = request.FILES['profile_pic']
                fs = FileSystemStorage()
                filename = fs.save(profile_pic.name, profile_pic)
                profile_pic_url = fs.url(filename)
            else:
                profile_pic_url = None

            try:
                # First Update into Custom User Model
                user = CustomUser.objects.get(id=suppliers_id)
                user.first_name = first_name
                user.last_name = last_name
                user.email = email
                user.username = username
                user.save()

                # Then Update Suppliers Table
                student_model = Suppliers.objects.get(admin=suppliers_id)
                student_model.address = address

                coffee_type = Courses.objects.get(id=course_id)
                student_model.course_id = coffee_type

                session_year_obj = SessionYearModel.objects.get(id=session_year_id)
                student_model.session_year_id = session_year_obj

                student_model.gender = gender
                if profile_pic_url != None:
                    student_model.profile_pic = profile_pic_url
                student_model.save()
                # Delete suppliers_id SESSION after the data is updated
                del request.session['suppliers_id']

                messages.success(request, "Supplier Updated Successfully!")
                return redirect('/edit_suppliers/'+suppliers_id)
            except:
                messages.success(request, "Failed to Uupdate Supplier.")
                return redirect('/edit_suppliers/'+suppliers_id)
        else:
            return redirect('/edit_suppliers/'+suppliers_id)


def delete_suppliers(request, suppliers_id):
    supplier = Suppliers.objects.get(admin=suppliers_id)
    try:
        supplier.delete()
        messages.success(request, "Supplier Deleted Successfully.")
        return redirect('manage_suppliers')
    except:
        messages.error(request, "Failed to Delete Supplier.")
        return redirect('manage_suppliers')


def add_subject(request):
    courses = Courses.objects.all()
    staffs = CustomUser.objects.filter(user_type='2')
    context = {
        "courses": courses,
        "staffs": staffs
    }
    return render(request, 'admin_template/add_subject_template.html', context)



def add_subject_save(request):
    if request.method != "POST":
        messages.error(request, "Method Not Allowed!")
        return redirect('add_subject')
    else:
        subject_name = request.POST.get('batch')

        course_id = request.POST.get('coffee_type')
        coffee_type = Courses.objects.get(id=course_id)
        
        clerk_id = request.POST.get('clerk')
        clerk = CustomUser.objects.get(id=clerk_id)

        try:
            batch = Subjects(subject_name=subject_name, course_id=coffee_type, clerk_id=clerk)
            batch.save()
            messages.success(request, "Batch Added Successfully!")
            return redirect('add_subject')
        except:
            messages.error(request, "Failed to Add Batch!")
            return redirect('add_subject')


def manage_subject(request):
    subjects = Subjects.objects.all()
    context = {
        "subjects": subjects
    }
    return render(request, 'admin_template/manage_subject_template.html', context)


def edit_subject(request, subject_id):
    batch = Subjects.objects.get(id=subject_id)
    courses = Courses.objects.all()
    staffs = CustomUser.objects.filter(user_type='2')
    context = {
        "batch": batch,
        "courses": courses,
        "staffs": staffs,
        "id": subject_id
    }
    return render(request, 'admin_template/edit_subject_template.html', context)


def edit_subject_save(request):
    if request.method != "POST":
        HttpResponse("Invalid Method.")
    else:
        subject_id = request.POST.get('subject_id')
        subject_name = request.POST.get('batch')
        course_id = request.POST.get('coffee_type')
        clerk_id = request.POST.get('clerk')

        try:
            batch = Subjects.objects.get(id=subject_id)
            batch.subject_name = subject_name

            coffee_type = Courses.objects.get(id=course_id)
            batch.course_id = coffee_type

            clerk = CustomUser.objects.get(id=clerk_id)
            batch.clerk_id = clerk
            
            batch.save()

            messages.success(request, "Batch Updated Successfully.")
            # return redirect('/edit_subject/'+subject_id)
            return HttpResponseRedirect(reverse("edit_subject", kwargs={"subject_id":subject_id}))

        except:
            messages.error(request, "Failed to Update Batch.")
            return HttpResponseRedirect(reverse("edit_subject", kwargs={"subject_id":subject_id}))
            # return redirect('/edit_subject/'+subject_id)



def delete_subject(request, subject_id):
    batch = Subjects.objects.get(id=subject_id)
    try:
        batch.delete()
        messages.success(request, "Batch Deleted Successfully.")
        return redirect('manage_subject')
    except:
        messages.error(request, "Failed to Delete Batch.")
        return redirect('manage_subject')


@csrf_exempt
def check_email_exist(request):
    email = request.POST.get("email")
    user_obj = CustomUser.objects.filter(email=email).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)


@csrf_exempt
def check_username_exist(request):
    username = request.POST.get("username")
    user_obj = CustomUser.objects.filter(username=username).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)



def suppliers_feedback_message(request):
    feedbacks = FeedBackSuppliers.objects.all()
    context = {
        "feedbacks": feedbacks
    }
    return render(request, 'admin_template/student_feedback_template.html', context)


@csrf_exempt
def suppliers_feedback_message_reply(request):
    feedback_id = request.POST.get('id')
    feedback_reply = request.POST.get('reply')

    try:
        feedback = FeedBackSuppliers.objects.get(id=feedback_id)
        feedback.feedback_reply = feedback_reply
        feedback.save()
        return HttpResponse("True")

    except:
        return HttpResponse("False")


def clerk_feedback_message(request):
    feedbacks = FeedBackClerk.objects.all()
    context = {
        "feedbacks": feedbacks
    }
    return render(request, 'admin_template/staff_feedback_template.html', context)


@csrf_exempt
def clerk_feedback_message_reply(request):
    feedback_id = request.POST.get('id')
    feedback_reply = request.POST.get('reply')

    try:
        feedback = FeedBackClerk.objects.get(id=feedback_id)
        feedback.feedback_reply = feedback_reply
        feedback.save()
        return HttpResponse("True")

    except:
        return HttpResponse("False")


def supplier_leave_view(request):
    leaves = LeaveReportSuppliers.objects.all()
    context = {
        "leaves": leaves
    }
    return render(request, 'admin_template/supplier_leave_view.html', context)

def supplier_leave_approve(request, leave_id):
    leave = LeaveReportSuppliers.objects.get(id=leave_id)
    leave.leave_status = 1
    leave.save()
    return redirect('supplier_leave_view')


def supplier_leave_reject(request, leave_id):
    leave = LeaveReportSuppliers.objects.get(id=leave_id)
    leave.leave_status = 2
    leave.save()
    return redirect('supplier_leave_view')


def clerk_leave_view(request):
    leaves = LeaveReportClerk.objects.all()
    context = {
        "leaves": leaves
    }
    return render(request, 'admin_template/clerk_leave_view.html', context)


def clerk_leave_approve(request, leave_id):
    leave = LeaveReportClerk.objects.get(id=leave_id)
    leave.leave_status = 1
    leave.save()
    return redirect('clerk_leave_view')


def clerk_leave_reject(request, leave_id):
    leave = LeaveReportClerk.objects.get(id=leave_id)
    leave.leave_status = 2
    leave.save()
    return redirect('clerk_leave_view')


def admin_view_attendance(request):
    subjects = Subjects.objects.all()
    session_years = SessionYearModel.objects.all()
    context = {
        "subjects": subjects,
        "session_years": session_years
    }
    return render(request, "admin_template/admin_view_attendance.html", context)


@csrf_exempt
def admin_get_attendance_dates(request):
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
def admin_get_attendance_student(request):
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


def admin_profile(request):
    user = CustomUser.objects.get(id=request.user.id)

    context={
        "user": user
    }
    return render(request, 'admin_template/admin_profile.html', context)


def admin_profile_update(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('admin_profile')
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')

        try:
            customuser = CustomUser.objects.get(id=request.user.id)
            customuser.first_name = first_name
            customuser.last_name = last_name
            if password != None and password != "":
                customuser.set_password(password)
            customuser.save()
            messages.success(request, "Profile Updated Successfully")
            return redirect('admin_profile')
        except:
            messages.error(request, "Failed to Update Profile")
            return redirect('admin_profile')
    


def clerk_profile(request):
    pass


def supplier_profile(requtest):
    pass



