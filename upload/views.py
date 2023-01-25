from django.shortcuts import render, redirect
from django.http import HttpResponse
from .functions import handle_uploaded_file
from django.core.files.storage import FileSystemStorage

from .forms import StudentForm


def index(request):
    if request.method == 'POST':

        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        email = request.POST['email']
        img = request.FILES['file']

        fs = FileSystemStorage(location='media/', base_url='media/')
        fs.save(img.name, img)

        print(firstname)
        print(lastname)
        print(email)

        print(img)

        return redirect('upload')

        # student = StudentForm(request.POST, request.FILES)
        # if student.is_valid():
        #     pass
        #
        #     myfile = request.FILES['myfile']
        #     fs = FileSystemStorage(location='media/screening_ab1', base_url='media/screening_ab1')
        #     # FileSystemStorage.save(file_name, file_content)
        #     filename = fs.save(myfile.name, myfile)
        #     uploaded_file_url = fs.url(filename)
        #     return render(request, 'upload.html', {
        #         'uploaded_file_url': uploaded_file_url
        #     })

    else:
        student = StudentForm()
        return render(request,"upload.html",{'form':student})

