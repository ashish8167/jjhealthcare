from django.urls import path
from . import views
from .views import add_patient
urlpatterns = [
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    # path('add-patient/', views.add_patient),
    path("add-patient/", add_patient, name="add_patient"),
    path('pharmacy/', views.pharmacy, name='pharmacy'),
    path('non_medical/', views.non_medical, name='non_medical'),
    path('lab/', views.lab, name='lab'),
    path('doctor/', views.doctor, name='doctor'),
    path('room/', views.room, name='room'),
    path("other/", views.other, name="other"),
    # path('print/<str:category>/', views.print_page),
    path('delete-patient/', views.delete_patient, name='delete_patient'),
    path('print/<int:patient_id>/<str:category>/', views.print_page),
    path("patient/<int:id>/", views.patient_dashboard, name="patient_dashboard"),
    path('logout/', views.logout_view),
    path('delete/<int:id>/', views.delete_record, name='delete'),
    path('edit/<int:id>/', views.edit_record, name='edit'),
    path('set-patient/<int:id>/', views.set_patient, name='set_patient'),

]