from django.shortcuts import render, redirect, get_object_or_404
from .models import Patient, Billing
from .forms import PatientForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import date
from django.utils import timezone
from django.shortcuts import render, redirect
from .models import Patient
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from datetime import date

# 🔐 LOGIN
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})

    return render(request, 'login.html')


# 🔓 LOGOUT
def logout_view(request):
    logout(request)
    return redirect('login')


# 🏠 DASHBOARD
@login_required
def dashboard(request):
    return render(request, 'dashboard.html')


# 👤 ADD PATIENT
@login_required
def add_patient(request):
    form = PatientForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect('dashboard')

    return render(request, 'add_patient.html', {'form': form})


# 💊 COMMON BILLING FUNCTION
@login_required
def billing_page(request, category):
    patients = Patient.objects.all()
    # records = Billing.objects.filter(category=category).order_by('-id')
    selected_patient = request.session.get('selected_patient')

    if selected_patient:
        records = Billing.objects.filter(
            category=category,
            patient_id=selected_patient
        ).order_by('-id')
    else:
        records = Billing.objects.none()  # show nothing if not selected

    # 🔥 DROPDOWN LISTS
    pharmacy_items = [
        "IV SET", "IV CANULA", "EASY FIX", "NS 100 ML",
        "TRACHEOSTRACY TUBE", "OXYGEN MASK", "NEBULIZER KIT",
        "FOLEYS TRACE CATHETER", "DNS", "RESP HYPERNEB 3%",
        "BANDAGES", "FEEDING TUBE", "NEEDLE", "SYRING", "INSULIN SYRING"
    ]

    lab_tests = [
        "CBP", "CRP", "SERUM ELECTROLYTES",
        "SR. ELECTROLYTES", "ABG"
    ]

    doctor_items = [
        "DR. CONSULTATION"
    ]

    non_medical_items = [
        "GLOVE BOX", "UNDER PADS", "WET WIPES",
        "TISSUE ROLL", "DIAPER", "UROMETER"
    ]

    other_items = [
        "SERVICE CHARGE", "NURSING CARE", "MISC"
    ]
    
    

    if request.method == 'POST':

        patient_id = request.POST.get('patient')
        request.session['selected_patient'] = patient_id
        if not patient_id:
            return render(request, 'billing.html', {
                'error': 'Please select patient',
            })
        # 🔥 handle dropdown + custom
        item = request.POST.get('item')
        custom = request.POST.get('custom_item')

        item_name = custom if item == "other" else item
        # 🔥 ROOM CATEGORY
        if category == "room":

            from_date = request.POST.get('from_date')
            to_date = request.POST.get('to_date')

            # ✅ FORCE VALID DATE
            if from_date:
                final_date = from_date
            else:
                final_date = timezone.now().date()

            Billing.objects.create(
                patient_id=patient_id,
                category=category,
                date=final_date,   # ✅ ALWAYS VALID
                from_date=from_date or None,
                to_date=to_date or None,
                item_name=item_name,
                amount=int(request.POST.get('amount') or 0),
                paid_amount=int(request.POST.get('paid') or 0)
            )
        # 🔥 OTHER CATEGORIES
        else:
            qty = int(request.POST.get('qty') or 1)
            rate = int(request.POST.get('amount') or 0)

            # apply qty only for selected categories
            if category not in ["doctor", "other", "room"]:
                final_amount = qty * rate
            else:
                final_amount = rate
                qty = ""   # no qty for these

            Billing.objects.create(
                patient_id=patient_id,
                category=category,
                date=request.POST.get('date') or timezone.now().date(),
                item_name=item_name,
                quantity=qty,
                amount=final_amount,
                paid_amount=int(request.POST.get('paid') or 0)
            )

        return redirect(category)

    # totals
    # total_amount = sum(r.amount for r in records)
    # total_paid = sum(r.paid_amount for r in records)
    # balance = total_amount - total_paid
    total_amount = 0
    total_paid = 0
    for r in records:

        if category == "room":
            if r.from_date and r.to_date:
                days = (r.to_date - r.from_date).days + 1
                days = max(days, 1)

                r.total_days = days
                r.calculated_amount = days * r.amount

                total_amount += r.calculated_amount
            else:
                r.total_days = 1
                r.calculated_amount = r.amount
                total_amount += r.amount

        else:
            r.calculated_amount = r.amount
            total_amount += r.amount

        total_paid += r.paid_amount or 0

    balance = total_amount - total_paid

    selected_patient_id = request.session.get('selected_patient')

    selected_patient_name = None
    if selected_patient_id:
        patient_obj = Patient.objects.filter(id=selected_patient_id).first()
        if patient_obj:
            selected_patient_name = patient_obj.name



    return render(request, 'billing.html', {
        'patients': patients,
        'records': records,
        'today': timezone.now().date(),
        'category': category,

        # 👇 ADD THESE
        'pharmacy_items': pharmacy_items,
        'lab_tests': lab_tests,
        'doctor_items': doctor_items,
        'non_medical_items': non_medical_items,
        'other_items': other_items,

        'total_amount': total_amount,
        'total_paid': total_paid,
        'balance': balance,
        'selected_patient_name': selected_patient_name,
    })

# ✏️ INLINE AUTO EDIT (NO SAVE BUTTON)
@login_required
def edit_record(request, id):
    record = get_object_or_404(Billing, id=id)

    if request.method == 'POST':

        # 🔥 ROOM CATEGORY FIX
        if record.category == "room":
            record.from_date = request.POST.get('from_date') or None
            record.to_date = request.POST.get('to_date') or None

        else:
            date_val = request.POST.get('date')
            if date_val:
                record.date = date_val

        record.item_name = request.POST.get('item', '')
        qty = int(request.POST.get('qty') or 1)
        rate = int(request.POST.get('amount') or 0)

        if record.category not in ["doctor", "other", "room"]:
            record.quantity = qty
            record.amount = qty * rate
        else:
            record.quantity = ""
            record.amount = rate
        record.paid_amount = int(request.POST.get('paid') or 0)

        record.save()

    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))


# 🗑 DELETE
@login_required
def delete_record(request, id):
    record = get_object_or_404(Billing, id=id)
    category = record.category
    record.delete()
    return redirect(category)


# 🖨 PRINT ALL
@login_required
def print_page(request, patient_id, category):
    patient = get_object_or_404(Patient, id=patient_id)

    records = Billing.objects.filter(
        patient=patient,
        category=category
    )

    # total_amount = sum(r.amount for r in records)
    # total_paid = sum(r.paid_amount for r in records)
    total_amount = 0
    total_paid = 0
    for r in records:

        if category == "room":
            if r.from_date and r.to_date:
                days = (r.to_date - r.from_date).days + 1
                days = max(days, 1)

                r.total_days = days
                r.calculated_amount = days * r.amount

                total_amount += r.calculated_amount
            else:
                r.total_days = 1
                r.calculated_amount = r.amount
                total_amount += r.amount

        else:
            r.calculated_amount = r.amount
            total_amount += r.amount

        total_paid += r.paid_amount or 0

    balance = total_amount - total_paid


    return render(request, 'print.html', {
        'records': records,
        'patient': patient,   # 🔥 IMPORTANT
        'total_amount': total_amount,
        'total_paid': total_paid,
        'balance': total_amount - total_paid,
        'category': category
    })


# 🔗 ROUTES
@login_required
def pharmacy(request):
    return billing_page(request, 'pharmacy')


@login_required
def non_medical(request):
    return billing_page(request, 'non_medical')


@login_required
def lab(request):
    return billing_page(request, 'lab')


@login_required
def doctor(request):
    return billing_page(request, 'doctor')


@login_required
def room(request):
    return billing_page(request, 'room')


@login_required
def other(request):
    return billing_page(request, 'other')

@login_required
def patient_dashboard(request, id):
    patient = get_object_or_404(Patient, id=id)

    records = Billing.objects.filter(patient=patient)

    pharmacy = records.filter(category='pharmacy')
    lab = records.filter(category='lab')
    doctor = records.filter(category='doctor')
    room = records.filter(category='room')
    non_medical = records.filter(category='non_medical')
    other = records.filter(category='other')

    total_amount = sum(r.amount for r in records)
    total_paid = sum(r.paid_amount for r in records)
    balance = total_amount - total_paid

    return render(request, 'patient_dashboard.html', {
        'patient': patient,
        'pharmacy': pharmacy,
        'lab': lab,
        'doctor': doctor,
        'room': room,
        'non_medical': non_medical,
        'other': other,
        'total_amount': total_amount,
        'total_paid': total_paid,
        'balance': balance
    })

@login_required
def delete_patient(request):
    patient_id = request.GET.get('id')

    if patient_id:
        patient = Patient.objects.get(id=patient_id)

        # 🔥 DELETE ALL RELATED DATA
        Billing.objects.filter(patient=patient).delete()
        patient.delete()

        # ✅ REMOVE FROM SESSION IF SAME
        if request.session.get('selected_patient') == str(patient_id):
            del request.session['selected_patient']

        return redirect('dashboard')
    

@login_required
def set_patient(request, id):
    request.session['selected_patient'] = str(id)

    # go back to same page
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))    


@login_required
def download_pdf(request, patient_id, category):
    patient = get_object_or_404(Patient, id=patient_id)

    records = Billing.objects.filter(
        patient=patient,
        category=category
    )

    # total_amount = sum(r.amount for r in records)
    # total_paid = sum(r.paid_amount for r in records)
    total_amount = 0
    total_paid = 0
    for r in records:

        if category == "room":
            if r.from_date and r.to_date:
                days = (r.to_date - r.from_date).days + 1
                days = max(days, 1)

                r.total_days = days
                r.calculated_amount = days * r.amount

                total_amount += r.calculated_amount
            else:
                r.total_days = 1
                r.calculated_amount = r.amount
                total_amount += r.amount

        else:
            r.calculated_amount = r.amount
            total_amount += r.amount

        total_paid += r.paid_amount or 0

    balance = total_amount - total_paid    

    html_string = render_to_string('print.html', {
        'records': records,
        'patient': patient,
        'total_amount': total_amount,
        'total_paid': total_paid,
        'balance': total_amount - total_paid,
        'category': category
    })

    pdf_file = HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')

    safe_name = patient.name.replace(" ", "_")
    today = date.today().strftime("%d-%b-%Y")

    response['Content-Disposition'] = f'attachment; filename="Bill_{safe_name}_{category}_{today}.pdf"'
    return response