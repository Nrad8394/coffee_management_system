from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.core.files.storage import FileSystemStorage #To upload Profile Picture
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
import json

from .models import CustomUser, Clerk, Coffee_types, Batch, Suppliers, SeasonYearModel, FeedBackSuppliers, FeedBackClerk, LeaveReportSuppliers, LeaveReportClerk, Attendance, AttendanceReport
from .forms import AddSupplierForm, EditSupplierForm

def admin_dashboard(request):
    return render(request, "admin_template/admin_dashboard.html")
    

def admin_home(request):
    all_supplier_count = Suppliers.objects.all().count()
    batch_count = Batch.objects.all().count()
    coffee_types_count = Coffee_types.objects.all().count()
    clerk_count = Clerk.objects.all().count()

    # Total Batch and suppliers in Each Coffee_type
    coffee_types_all = Coffee_types.objects.all()
    coffee_types_name_list = []
    batch_count_list = []
    supplier_count_list_in_coffee_types = []

    for coffee_type in coffee_types_all:
        batchs = Batch.objects.filter(coffee_types_id=coffee_type.id).count()
        suppliers = Suppliers.objects.filter(coffee_types_id=coffee_type.id).count()
        coffee_types_name_list.append(coffee_type.coffee_types_name)
        batch_count_list.append(batchs)
        supplier_count_list_in_coffee_types.append(suppliers)
    
    batch_all = Batch.objects.all()
    batch_list = []
    supplier_count_list_in_batch = []
    for batch in batch_all:
        coffee_type = Coffee_types.objects.get(id=batch.coffee_types_id.id)
        supplier_count = Suppliers.objects.filter(coffee_types_id=coffee_type.id).count()
        batch_list.append(batch.batch_name)
        supplier_count_list_in_batch.append(supplier_count)
    
    # For Clerk
    clerk_attendance_present_list=[]
    clerk_attendance_leave_list=[]
    clerk_name_list=[]

    clerks = Clerk.objects.all()
    for clerk in clerks:
        batch_ids = Batch.objects.filter(clerk_id=clerk.user.id)
        attendance = Attendance.objects.filter(batch_id__in=batch_ids).count()
        leaves = LeaveReportClerk.objects.filter(clerk_id=clerk.id, leave_status=1).count()
        clerk_attendance_present_list.append(attendance)
        clerk_attendance_leave_list.append(leaves)
        clerk_name_list.append(clerk.user.first_name)

    # For Suppliers
    supplier_attendance_present_list=[]
    supplier_attendance_leave_list=[]
    supplier_name_list=[]

    suppliers = Suppliers.objects.all()
    for supplier in suppliers:
        attendance = AttendanceReport.objects.filter(suppliers_id=supplier.id, status=True).count()
        absent = AttendanceReport.objects.filter(suppliers_id=supplier.id, status=False).count()
        leaves = LeaveReportSuppliers.objects.filter(suppliers_id=supplier.id, leave_status=1).count()
        supplier_attendance_present_list.append(attendance)
        supplier_attendance_leave_list.append(leaves+absent)
        supplier_name_list.append(supplier.user.first_name)


    context={
        "all_supplier_count": all_supplier_count,
        "batch_count": batch_count,
        "coffee_types_count": coffee_types_count,
        "clerk_count": clerk_count,
        "coffee_types_name_list": coffee_types_name_list,
        "batch_count_list": batch_count_list,
        "supplier_count_list_in_coffee_types": supplier_count_list_in_coffee_types,
        "batch_list": batch_list,
        "supplier_count_list_in_batch": supplier_count_list_in_batch,
        "clerk_attendance_present_list": clerk_attendance_present_list,
        "clerk_attendance_leave_list": clerk_attendance_leave_list,
        "clerk_name_list": clerk_name_list,
        "supplier_attendance_present_list": supplier_attendance_present_list,
        "supplier_attendance_leave_list": supplier_attendance_leave_list,
        "supplier_name_list": supplier_name_list,
    }
    return render(request, "admin_template/home_content.html", context)


def add_clerk(request):
    return render(request, "admin_template/add_clerk_template.html")


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
           
            user.clerk.address = address
            user.save()
            
            messages.success(request, "Clerk Added Successfully!")
            return redirect('add_clerk')
        except Exception as e:
            print(e)
            messages.error(request, "Failed to Add Clerk!")
            return redirect('add_clerk')



def manage_clerk(request):
    clerks = Clerk.objects.all()
    context = {
        "clerks": clerks
    }
    return render(request, "admin_template/manage_clerk_template.html", context)


def edit_clerk(request, clerk_id):
    clerk = Clerk.objects.get(user=clerk_id)

    context = {
        "clerk": clerk,
        "id": clerk_id
    }
    return render(request, "admin_template/edit_clerk_template.html", context)


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
            clerk_model = Clerk.objects.get(user=clerk_id)
            clerk_model.address = address
            clerk_model.save()

            messages.success(request, "Clerk Updated Successfully.")
            return redirect('/edit_clerk/'+clerk_id)

        except:
            messages.error(request, "Failed to Update Clerk.")
            return redirect('/edit_clerk/'+clerk_id)



def delete_clerk(request, clerk_id):
    clerk = Clerk.objects.get(user=clerk_id)
    try:
        clerk.delete()
        messages.success(request, "Clerk Deleted Successfully.")
        return redirect('manage_clerk')
    except:
        messages.error(request, "Failed to Delete Clerk.")
        return redirect('manage_clerk')




def add_coffee_types(request):
    return render(request, "admin_template/add_coffee_types_template.html")


def add_coffee_types_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('add_coffee_types')
    else:
        coffee_type = request.POST.get('coffee_type')
        try:
            coffee_types_model = Coffee_types(coffee_types_name=coffee_type)
            coffee_types_model.save()
            messages.success(request, "Coffee_type Added Successfully!")
            return redirect('add_coffee_types')
        except:
            messages.error(request, "Failed to Add Coffee_type!")
            return redirect('add_coffee_types')


def manage_coffee_types(request):
    coffee_types = Coffee_types.objects.all()
    context = {
        "coffee_types": coffee_types
    }
    return render(request, 'admin_template/manage_coffee_types_template.html', context)


def edit_coffee_types(request, coffee_types_id):
    coffee_type = Coffee_types.objects.get(id=coffee_types_id)
    context = {
        "coffee_type": coffee_type,
        "id": coffee_types_id
    }
    return render(request, 'admin_template/edit_coffee_types_template.html', context)


def edit_coffee_types_save(request):
    if request.method != "POST":
        HttpResponse("Invalid Method")
    else:
        coffee_types_id = request.POST.get('coffee_types_id')
        coffee_types_name = request.POST.get('coffee_type')

        try:
            coffee_type = Coffee_types.objects.get(id=coffee_types_id)
            coffee_type.coffee_types_name = coffee_types_name
            coffee_type.save()

            messages.success(request, "Coffee_type Updated Successfully.")
            return redirect('/edit_coffee_types/'+coffee_types_id)

        except:
            messages.error(request, "Failed to Update Coffee_type.")
            return redirect('/edit_coffee_types/'+coffee_types_id)


def delete_coffee_types(request, coffee_types_id):
    coffee_type = Coffee_types.objects.get(id=coffee_types_id)
    try:
        coffee_type.delete()
        messages.success(request, "Coffee_type Deleted Successfully.")
        return redirect('manage_coffee_types')
    except:
        messages.error(request, "Failed to Delete Coffee_type.")
        return redirect('manage_coffee_types')


def manage_season(request):
    season_years = SeasonYearModel.objects.all()
    context = {
        "season_years": season_years
    }
    return render(request, "admin_template/manage_season_template.html", context)


def add_season(request):
    return render(request, "admin_template/add_season_template.html")


def add_season_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('add_coffee_types')
    else:
        season_start_year = request.POST.get('season_start_year')
        season_end_year = request.POST.get('season_end_year')

        try:
            seasonyear = SeasonYearModel(season_start_year=season_start_year, season_end_year=season_end_year)
            seasonyear.save()
            messages.success(request, "Season Year added Successfully!")
            return redirect("add_season")
        except:
            messages.error(request, "Failed to Add Season Year")
            return redirect("add_season")


def edit_season(request, season_id):
    season_year = SeasonYearModel.objects.get(id=season_id)
    context = {
        "season_year": season_year
    }
    return render(request, "admin_template/edit_season_template.html", context)


def edit_season_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('manage_season')
    else:
        season_id = request.POST.get('season_id')
        season_start_year = request.POST.get('season_start_year')
        season_end_year = request.POST.get('season_end_year')

        try:
            season_year = SeasonYearModel.objects.get(id=season_id)
            season_year.season_start_year = season_start_year
            season_year.season_end_year = season_end_year
            season_year.save()

            messages.success(request, "Season Year Updated Successfully.")
            return redirect('/edit_season/'+season_id)
        except:
            messages.error(request, "Failed to Update Season Year.")
            return redirect('/edit_season/'+season_id)


def delete_season(request, season_id):
    season = SeasonYearModel.objects.get(id=season_id)
    try:
        season.delete()
        messages.success(request, "Season Deleted Successfully.")
        return redirect('manage_season')
    except:
        messages.error(request, "Failed to Delete Season.")
        return redirect('manage_season')


def add_suppliers(request):
    form = AddSupplierForm()
    context = {
        "form": form
    }
    return render(request, 'admin_template/add_supplier_template.html', context)




def add_suppliers_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('add_suppliers')
    else:
        form = AddSupplierForm(request.POST, request.FILES)

        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            address = form.cleaned_data['address']
            season_year_id = form.cleaned_data['season_year_id']
            coffee_types_id = form.cleaned_data['coffee_types_id']
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
                user.suppliers.address = address

                coffee_types_obj = Coffee_types.objects.get(id=coffee_types_id)
                user.suppliers.coffee_types_id = coffee_types_obj

                season_year_obj = SeasonYearModel.objects.get(id=season_year_id)
                user.suppliers.season_year_id = season_year_obj

                user.suppliers.gender = gender
                # user.suppliers.profile_pic = profile_pic_url
                user.save()
                messages.success(request, "Supplier Added Successfully!")
                return redirect('add_suppliers')
            except:
                messages.error(request, "Failed to Add Supplier!")
                return redirect('add_suppliers')
        else:
            return redirect('add_suppliers')


def manage_suppliers(request):
    suppliers = Suppliers.objects.all()
    context = {
        "suppliers": suppliers
    }
    return render(request, 'admin_template/manage_supplier_template.html', context)


def edit_suppliers(request, suppliers_id):
    # Adding Supplier ID into Season Variable
    request.season['suppliers_id'] = suppliers_id

    supplier = Suppliers.objects.get(user=suppliers_id)
    form = EditSupplierForm()
    # Filling the form with Data from Database
    form.fields['email'].initial = supplier.user.email
    form.fields['username'].initial = supplier.user.username
    form.fields['first_name'].initial = supplier.user.first_name
    form.fields['last_name'].initial = supplier.user.last_name
    form.fields['address'].initial = supplier.address
    form.fields['coffee_types_id'].initial = supplier.coffee_types_id.id
    form.fields['gender'].initial = supplier.gender
    form.fields['season_year_id'].initial = supplier.season_year_id.id

    context = {
        "id": suppliers_id,
        "username": supplier.user.username,
        "form": form
    }
    return render(request, "admin_template/edit_supplier_template.html", context)


def edit_suppliers_save(request):
    if request.method != "POST":
        return HttpResponse("Invalid Method!")
    else:
        suppliers_id = request.season.get('suppliers_id')
        if suppliers_id == None:
            return redirect('/manage_suppliers')

        form = EditSupplierForm(request.POST, request.FILES)
        if form.is_valid():
            email = form.cleaned_data['email']
            username = form.cleaned_data['username']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            address = form.cleaned_data['address']
            coffee_types_id = form.cleaned_data['coffee_types_id']
            gender = form.cleaned_data['gender']
            season_year_id = form.cleaned_data['season_year_id']

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
                supplier_model = Suppliers.objects.get(user=suppliers_id)
                supplier_model.address = address

                coffee_type = Coffee_types.objects.get(id=coffee_types_id)
                supplier_model.coffee_types_id = coffee_type

                season_year_obj = SeasonYearModel.objects.get(id=season_year_id)
                supplier_model.season_year_id = season_year_obj

                supplier_model.gender = gender
                if profile_pic_url != None:
                    supplier_model.profile_pic = profile_pic_url
                supplier_model.save()
                # Delete suppliers_id SESSION after the data is updated
                del request.season['suppliers_id']

                messages.success(request, "Supplier Updated Successfully!")
                return redirect('/edit_suppliers/'+suppliers_id)
            except:
                messages.success(request, "Failed to Uupdate Supplier.")
                return redirect('/edit_suppliers/'+suppliers_id)
        else:
            return redirect('/edit_suppliers/'+suppliers_id)


def delete_suppliers(request, suppliers_id):
    supplier = Suppliers.objects.get(user=suppliers_id)
    try:
        supplier.delete()
        messages.success(request, "Supplier Deleted Successfully.")
        return redirect('manage_suppliers')
    except:
        messages.error(request, "Failed to Delete Supplier.")
        return redirect('manage_suppliers')


def add_batch(request):
    coffee_types = Coffee_types.objects.all()
    clerks = CustomUser.objects.filter(user_type='2')
    context = {
        "coffee_types": coffee_types,
        "clerks": clerks
    }
    return render(request, 'admin_template/add_batch_template.html', context)



def add_batch_save(request):
    if request.method != "POST":
        messages.error(request, "Method Not Allowed!")
        return redirect('add_batch')
    else:
        batch_name = request.POST.get('batch')

        coffee_types_id = request.POST.get('coffee_type')
        coffee_type = Coffee_types.objects.get(id=coffee_types_id)
        
        clerk_id = request.POST.get('clerk')
        clerk = CustomUser.objects.get(id=clerk_id)

        try:
            batch = Batch(batch_name=batch_name, coffee_types_id=coffee_type, clerk_id=clerk)
            batch.save()
            messages.success(request, "Batch Added Successfully!")
            return redirect('add_batch')
        except:
            messages.error(request, "Failed to Add Batch!")
            return redirect('add_batch')


def manage_batch(request):
    batchs = Batch.objects.all()
    context = {
        "batchs": batchs
    }
    return render(request, 'admin_template/manage_batch_template.html', context)


def edit_batch(request, batch_id):
    batch = Batch.objects.get(id=batch_id)
    coffee_types = Coffee_types.objects.all()
    clerks = CustomUser.objects.filter(user_type='2')
    context = {
        "batch": batch,
        "coffee_types": coffee_types,
        "clerks": clerks,
        "id": batch_id
    }
    return render(request, 'admin_template/edit_batch_template.html', context)


def edit_batch_save(request):
    if request.method != "POST":
        HttpResponse("Invalid Method.")
    else:
        batch_id = request.POST.get('batch_id')
        batch_name = request.POST.get('batch')
        coffee_types_id = request.POST.get('coffee_type')
        clerk_id = request.POST.get('clerk')

        try:
            batch = Batch.objects.get(id=batch_id)
            batch.batch_name = batch_name

            coffee_type = Coffee_types.objects.get(id=coffee_types_id)
            batch.coffee_types_id = coffee_type

            clerk = CustomUser.objects.get(id=clerk_id)
            batch.clerk_id = clerk
            
            batch.save()

            messages.success(request, "Batch Updated Successfully.")
            # return redirect('/edit_batch/'+batch_id)
            return HttpResponseRedirect(reverse("edit_batch", kwargs={"batch_id":batch_id}))

        except:
            messages.error(request, "Failed to Update Batch.")
            return HttpResponseRedirect(reverse("edit_batch", kwargs={"batch_id":batch_id}))
            # return redirect('/edit_batch/'+batch_id)



def delete_batch(request, batch_id):
    batch = Batch.objects.get(id=batch_id)
    try:
        batch.delete()
        messages.success(request, "Batch Deleted Successfully.")
        return redirect('manage_batch')
    except:
        messages.error(request, "Failed to Delete Batch.")
        return redirect('manage_batch')


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
    return render(request, 'admin_template/supplier_feedback_template.html', context)


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
    return render(request, 'admin_template/clerk_feedback_template.html', context)


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
    batchs = Batch.objects.all()
    season_years = SeasonYearModel.objects.all()
    context = {
        "batchs": batchs,
        "season_years": season_years
    }
    return render(request, "admin_template/admin_view_attendance.html", context)


@csrf_exempt
def admin_get_attendance_dates(request):
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
def admin_get_attendance_supplier(request):
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



