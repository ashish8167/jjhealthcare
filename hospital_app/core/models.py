from django.db import models

class Patient(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    gender = models.CharField(max_length=10)
    phone = models.CharField(max_length=15)

    def __str__(self):
        return self.name


class Billing(models.Model):
    CATEGORY_CHOICES = [
        ('pharmacy', 'Pharmacy materials'),
        ('non_medical', 'Non Medical Items'),
        ('lab', 'Lab Investigation'),
        ('doctor', 'Doctor Visits'),
        ('room', 'Room Facility'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    date = models.DateField()
    from_date = models.DateField(null=True, blank=True)
    to_date = models.DateField(null=True, blank=True)
    item_name = models.CharField(max_length=200)
    quantity = models.CharField(max_length=50, blank=True)
    amount = models.IntegerField()
    paid_amount = models.IntegerField(default=0)
    doa = models.DateField(null=True, blank=True)
    def __str__(self):
        return f"{self.patient.name} - {self.category}"