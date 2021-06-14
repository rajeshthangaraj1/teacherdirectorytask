# Create your views here.
import csv
import pdb
import zipfile
from io import StringIO, BytesIO

from django.contrib.auth.models import User
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import Q
from django.views.generic import TemplateView
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response import Response

from teacher.models import Teacher
from teacher.serializer import TeacherSerializer, TeacherDetailSerializer


class TeacherListView(TemplateView):
    template_name = 'teacher_list.html'

    def get_context_data(self, **kwargs):
        return {"teachers": Teacher.objects.all()}


class TeacherProfileView(TemplateView):
    template_name = 'teacher_profile.html'

    def get_context_data(self, **kwargs):
        return {"teacher": Teacher.objects.get(pk=kwargs['pk'])}


class TeacherViewSet(viewsets.ModelViewSet):
    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TeacherDetailSerializer
        else:
            return TeacherSerializer

    def get_queryset(self):
        if self.request.method in SAFE_METHODS:
            return Teacher.objects.all()
        if self.request.user.is_staff:
            return Teacher.objects.all()
        elif self.request.user.is_authenticated:
            return Teacher.objects.filter(user=self.request.user)

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [permissions.AllowAny()]
        else:
            return [permissions.IsAuthenticated()]

    @action(detail=False, methods=['post'])
    def import_data(self, request):
        fs = request.FILES['file']
        zip = zipfile.ZipFile(fs)
        teacher_data = zip.read('Teachers.csv').decode('utf-8')
        csv_file = csv.reader(StringIO(teacher_data))
        i = 0
        errors = {}
        for row in csv_file:
            try:
                if i == 0:  # Skip header row
                    i += 1
                    continue
                if not row[0]:  # Skip if first name empty
                    continue
                try:
                    img = zip.read(row[2])
                    fn = row[2]
                    ff = 'image/jpeg' if fn.lower().endswith('jpg') or fn.lower().endswith('jepg') else 'image/png'
                except Exception as ex:
                    img = open('templates/default.jpg', 'rb').read()
                    fn = 'default.jpg'
                    ff = 'image/jpeg'
                img = BytesIO(img)
                imagefile = InMemoryUploadedFile(img, None, fn, ff, img.getbuffer().nbytes, None)
                user = User.objects.create(first_name=row[0], last_name=row[1], email=row[3], username=row[3])
                user.set_password(row[7])
                Teacher.objects.create(profile_pic=imagefile, phone=row[4], room_no=row[5],
                                       subjects=row[6].split(','), user=user)
            except Exception as ex:
                errors.update({f"{row[0]} {row[1]}": str(ex)})

        return Response(errors)

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        if 'last_name' in request.GET:
            qs = qs.filter(user__last_name__startswith=request.GET['last_name'])
        if 'search' in request.GET:
            qs = qs.filter(subjects__icontains=request.GET['search'])
        return Response(TeacherDetailSerializer(qs, many=True).data)


