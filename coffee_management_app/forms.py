from django import forms 
from django.forms import Form
from coffee_management_app.models import Coffee_types, SeasonYearModel


class DateInput(forms.DateInput):
    input_type = "date"


class AddSupplierForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=50, widget=forms.EmailInput(attrs={"class":"form-control"}))
    password = forms.CharField(label="Password", max_length=50, widget=forms.PasswordInput(attrs={"class":"form-control"}))
    first_name = forms.CharField(label="First Name", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    last_name = forms.CharField(label="Last Name", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    username = forms.CharField(label="Username", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    address = forms.CharField(label="Address", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))

    #For Displaying Coffee_types
    try:
        coffee_types = Coffee_types.objects.all()
        coffee_types_list = []
        for coffee_type in coffee_types:
            single_coffee_types = (coffee_type.id, coffee_type.coffee_types_name)
            coffee_types_list.append(single_coffee_types)
    except:
        coffee_types_list = []
    
    #For Displaying Season Years
    try:
        season_years = SeasonYearModel.objects.all()
        season_year_list = []
        for season_year in season_years:
            single_season_year = (season_year.id, str(season_year.season_start_year)+" to "+str(season_year.season_end_year))
            season_year_list.append(single_season_year)
            
    except:
        season_year_list = []
    
    gender_list = (
        ('Male','Male'),
        ('Female','Female')
    )
    
    coffee_types_id = forms.ChoiceField(label="Coffee_type", choices=coffee_types_list, widget=forms.Select(attrs={"class":"form-control"}))
    gender = forms.ChoiceField(label="Gender", choices=gender_list, widget=forms.Select(attrs={"class":"form-control"}))
    season_year_id = forms.ChoiceField(label="Season Year", choices=season_year_list, widget=forms.Select(attrs={"class":"form-control"}))
    # season_start_year = forms.DateField(label="Season Start", widget=DateInput(attrs={"class":"form-control"}))
    # season_end_year = forms.DateField(label="Season End", widget=DateInput(attrs={"class":"form-control"}))
    profile_pic = forms.FileField(label="Profile Pic", required=False, widget=forms.FileInput(attrs={"class":"form-control"}))



class EditSupplierForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=50, widget=forms.EmailInput(attrs={"class":"form-control"}))
    first_name = forms.CharField(label="First Name", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    last_name = forms.CharField(label="Last Name", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    username = forms.CharField(label="Username", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    address = forms.CharField(label="Address", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))

    #For Displaying Coffee_types
    try:
        coffee_types = Coffee_types.objects.all()
        coffee_types_list = []
        for coffee_type in coffee_types:
            single_coffee_types = (coffee_type.id, coffee_type.coffee_types_name)
            coffee_types_list.append(single_coffee_types)
    except:
        coffee_types_list = []

    #For Displaying Season Years
    try:
        season_years = SeasonYearModel.objects.all()
        season_year_list = []
        for season_year in season_years:
            single_season_year = (season_year.id, str(season_year.season_start_year)+" to "+str(season_year.season_end_year))
            season_year_list.append(single_season_year)
            
    except:
        season_year_list = []

    
    gender_list = (
        ('Male','Male'),
        ('Female','Female')
    )
    
    coffee_types_id = forms.ChoiceField(label="Coffee_type", choices=coffee_types_list, widget=forms.Select(attrs={"class":"form-control"}))
    gender = forms.ChoiceField(label="Gender", choices=gender_list, widget=forms.Select(attrs={"class":"form-control"}))
    season_year_id = forms.ChoiceField(label="Season Year", choices=season_year_list, widget=forms.Select(attrs={"class":"form-control"}))
    # season_start_year = forms.DateField(label="Season Start", widget=DateInput(attrs={"class":"form-control"}))
    # season_end_year = forms.DateField(label="Season End", widget=DateInput(attrs={"class":"form-control"}))
    profile_pic = forms.FileField(label="Profile Pic", required=False, widget=forms.FileInput(attrs={"class":"form-control"}))