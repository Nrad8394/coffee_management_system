# Django Supplier Management System (beta)
This is a Simple Supplier Management System Developed for Educational Purpose using Python (Django).
Feel free to make changes based on your requirements.

[Project Demo on YouTube](https://www.youtube.com/watch?v=kArCR96m7uo "Django Supplier Management System Demo")

I've created this project while learnging Django and followed tutorial series from **SuperCoders**

And if you like this project then ADD a STAR ⭐️  to this project 👆

## Features of this Project

### A. Admin Users Can
1. See Overall Summary Charts of Stuudents Performance, Clerk Perfomrances, Coffee_types, Batch, Leave, etc.
2. Manage Clerk (Add, Update and Delete)
3. Manage Suppliers (Add, Update and Delete)
4. Manage Coffee_type (Add, Update and Delete)
5. Manage Batch (Add, Update and Delete)
6. Manage Seasons (Add, Update and Delete)
7. View Supplier Attendance
8. Review and Reply Supplier/Clerk Feedback
9. Review (Approve/Reject) Supplier/Clerk Leave

### B. Clerk/Teachers Can
1. See the Overall Summary Charts related to their suppliers, their batch, leave status, etc.
2. Take/Update Suppliers Attendance
3. Add/Update Coffee data
4. Apply for Leave
5. Send Feedback to AdminManager

### C. Suppliers Can
1. See the Overall Summary Charts related to their attendance, their batch, leave status, etc.
2. View Attendance
3. View Coffee data
4. Apply for Leave
5. Send Feedback to AdminManager







## How to Install and Run this project?

### Pre-Requisites:
1. Install Git Version Control
[ https://git-scm.com/ ]

2. Install Python Latest Version
[ https://www.python.org/downloads/ ]

3. Install Pip (Package Manager)
[ https://pip.pypa.io/en/stable/installing/ ]

*Alternative to Pip is Homebrew*

### Installation
**1. Create a Folder where you want to save the project**

**2. Create a Virtual Environment and Activate**

Install Virtual Environment First
```
$  pip install virtualenv
```

Create Virtual Environment

For Windows
```
$  python -m venv venv
```
For Mac
```
$  python3 -m venv venv
```

Activate Virtual Environment

For Windows
```
$  source venv/scripts/activate
```

For Mac
```
$  source venv/bin/activate
```

**3. Clone this project**
```
$  git clone https://github.com/vijaythapa333/django-Supplier-management-system.git
```

Then, Enter the project
```
$  cd django-Supplier-management-system
```

**4. Install Requirements from 'requirements.txt'**
```python
$  pip install -r requirements.txt
```

**5. Add the hosts**

- Got to settings.py file 
- Then, On allowed hosts, Add [‘*’]. 
```python
ALLOWED_HOSTS = ['*']
```
*No need to change on Mac.*


**6. Now Run Server**

Command for PC:
```python
$ python manage.py runserver
```

Command for Mac:
```python
$ python3 manage.py runserver
```

**7. Login Credentials**

Create Super User (AdminManager)
```
$  python manage.py createsuperuser
```
Then Add Email, Username and Password

**or Use Default Credentials**

*For AdminManager /SuperAdmin*
Email: admin@gmail.com
Password: admin

*For Clerk*
Email: clerk@gmail.com
Password: clerk

*For Supplier*
Email: Supplier@gmail.com
Password: Supplier



## For Sponsor or Projects Enquiry
1. Email - hi@vijaythapa.com
2. LinkedIn - [vijaythapa](https://www.linkedin.com/in/vijaythapa "Vijay Thapa on LinkedIn")

