import os
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import User
from wardens.models import WardenProfile
from students.models import StudentProfile
from hostels.models import Hostel, Floor
from rooms.models import Room
from allocations.models import RoomAllocation
from fees.models import FeeCategory, FeeRecord, Payment
from complaints.models import Complaint, ComplaintHistory
from attendance.models import Attendance
from notices.models import Notice
from visitors.models import Visitor

class Command(BaseCommand):
    help = "Populates realistic hostel management database records for testing and demonstration"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding HostelPulse database records..."))

        # 1. Super Admin
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@hostel.edu',
                'first_name': 'Chief',
                'last_name': 'Administrator',
                'role': User.Role.SUPER_ADMIN,
                'is_staff': True,
                'is_superuser': True,
                'is_approved': True,
                'is_active': True,
                'phone': '+91 98765 43210'
            }
        )
        admin_user.set_password('AdminPassword123!')
        admin_user.save()
        self.stdout.write(self.style.SUCCESS("[OK] Super Admin: admin / AdminPassword123!"))

        # 2. Hostels & Floors
        h1, _ = Hostel.objects.get_or_create(
            code='BH-1',
            defaults={
                'name': 'Aryabhata Boys Hostel',
                'gender_type': Hostel.GenderType.BOYS,
                'address': 'North Campus, Engineering Block',
                'description': 'Modern residential complex with high-speed Wi-Fi, 24/7 security, and mess facility.',
                'contact_phone': '+91 98765 00001',
                'contact_email': 'bh1@hostel.edu',
                'is_active': True
            }
        )
        f1_0, _ = Floor.objects.get_or_create(hostel=h1, floor_number=0, defaults={'floor_name': 'Ground Floor'})
        f1_1, _ = Floor.objects.get_or_create(hostel=h1, floor_number=1, defaults={'floor_name': 'First Floor'})
        f1_2, _ = Floor.objects.get_or_create(hostel=h1, floor_number=2, defaults={'floor_name': 'Second Floor'})

        h2, _ = Hostel.objects.get_or_create(
            code='GH-1',
            defaults={
                'name': 'Sarojini Naidu Girls Hostel',
                'gender_type': Hostel.GenderType.GIRLS,
                'address': 'South Campus, Medical & Science Block',
                'description': 'Secure residence with surveillance, gymnasium, badminton court, and hygienic dining hall.',
                'contact_phone': '+91 98765 00002',
                'contact_email': 'gh1@hostel.edu',
                'is_active': True
            }
        )
        f2_0, _ = Floor.objects.get_or_create(hostel=h2, floor_number=0, defaults={'floor_name': 'Ground Floor'})
        f2_1, _ = Floor.objects.get_or_create(hostel=h2, floor_number=1, defaults={'floor_name': 'First Floor'})

        self.stdout.write(self.style.SUCCESS("[OK] Hostels & Floors initialized"))

        # 3. Wardens
        w1_user, _ = User.objects.get_or_create(
            username='warden1',
            defaults={
                'email': 'rajesh.warden@hostel.edu',
                'first_name': 'Dr. Rajesh',
                'last_name': 'Kumar',
                'role': User.Role.WARDEN,
                'is_staff': True,
                'is_approved': True,
                'is_active': True,
                'phone': '+91 98765 11111'
            }
        )
        w1_user.set_password('WardenPassword123!')
        w1_user.save()
        WardenProfile.objects.get_or_create(
            user=w1_user,
            defaults={
                'assigned_hostel': h1,
                'phone': '+91 98765 11111',
                'joining_date': timezone.now().date() - timezone.timedelta(days=365),
                'emergency_contact': '+91 98765 11199',
                'address': 'Hostel Campus Staff Quarters Q-1'
            }
        )

        w2_user, _ = User.objects.get_or_create(
            username='warden2',
            defaults={
                'email': 'sunita.warden@hostel.edu',
                'first_name': 'Prof. Sunita',
                'last_name': 'Verma',
                'role': User.Role.WARDEN,
                'is_staff': True,
                'is_approved': True,
                'is_active': True,
                'phone': '+91 98765 22222'
            }
        )
        w2_user.set_password('WardenPassword123!')
        w2_user.save()
        WardenProfile.objects.get_or_create(
            user=w2_user,
            defaults={
                'assigned_hostel': h2,
                'phone': '+91 98765 22222',
                'joining_date': timezone.now().date() - timezone.timedelta(days=200),
                'emergency_contact': '+91 98765 22299',
                'address': 'Hostel Campus Staff Quarters Q-2'
            }
        )
        self.stdout.write(self.style.SUCCESS("[OK] Wardens: warden1, warden2 / WardenPassword123!"))

        # 4. Rooms
        # Rooms in BH-1
        r101, _ = Room.objects.get_or_create(hostel=h1, room_number='101', defaults={'floor': f1_0, 'room_type': Room.RoomType.DOUBLE, 'capacity': 2, 'monthly_rent': Decimal('4500.00'), 'room_status': Room.RoomStatus.AVAILABLE})
        r102, _ = Room.objects.get_or_create(hostel=h1, room_number='102', defaults={'floor': f1_0, 'room_type': Room.RoomType.DOUBLE, 'capacity': 2, 'monthly_rent': Decimal('4500.00'), 'room_status': Room.RoomStatus.AVAILABLE})
        r201, _ = Room.objects.get_or_create(hostel=h1, room_number='201', defaults={'floor': f1_1, 'room_type': Room.RoomType.TRIPLE, 'capacity': 3, 'monthly_rent': Decimal('3800.00'), 'room_status': Room.RoomStatus.AVAILABLE})
        r202, _ = Room.objects.get_or_create(hostel=h1, room_number='202', defaults={'floor': f1_1, 'room_type': Room.RoomType.SINGLE, 'capacity': 1, 'monthly_rent': Decimal('6500.00'), 'room_status': Room.RoomStatus.AVAILABLE})
        r301, _ = Room.objects.get_or_create(hostel=h1, room_number='301', defaults={'floor': f1_2, 'room_type': Room.RoomType.FOUR, 'capacity': 4, 'monthly_rent': Decimal('3200.00'), 'room_status': Room.RoomStatus.AVAILABLE})

        # Rooms in GH-1
        rg101, _ = Room.objects.get_or_create(hostel=h2, room_number='101', defaults={'floor': f2_0, 'room_type': Room.RoomType.DOUBLE, 'capacity': 2, 'monthly_rent': Decimal('4800.00'), 'room_status': Room.RoomStatus.AVAILABLE})
        rg102, _ = Room.objects.get_or_create(hostel=h2, room_number='102', defaults={'floor': f2_0, 'room_type': Room.RoomType.DOUBLE, 'capacity': 2, 'monthly_rent': Decimal('4800.00'), 'room_status': Room.RoomStatus.AVAILABLE})
        rg201, _ = Room.objects.get_or_create(hostel=h2, room_number='201', defaults={'floor': f2_1, 'room_type': Room.RoomType.SINGLE, 'capacity': 1, 'monthly_rent': Decimal('7000.00'), 'room_status': Room.RoomStatus.AVAILABLE})
        self.stdout.write(self.style.SUCCESS("[OK] Hostel rooms generated"))

        # 5. Fee Categories
        fc_rent, _ = FeeCategory.objects.get_or_create(code='RENT', defaults={'name': 'Hostel Room Rent', 'default_amount': Decimal('4500.00')})
        fc_mess, _ = FeeCategory.objects.get_or_create(code='MESS', defaults={'name': 'Mess & Dining Charges', 'default_amount': Decimal('3200.00')})
        fc_elec, _ = FeeCategory.objects.get_or_create(code='ELECTRICITY', defaults={'name': 'Electricity & Utility Fee', 'default_amount': Decimal('600.00')})
        fc_maint, _ = FeeCategory.objects.get_or_create(code='MAINTENANCE', defaults={'name': 'Maintenance & Amenities', 'default_amount': Decimal('400.00')})
        fc_other, _ = FeeCategory.objects.get_or_create(code='OTHER', defaults={'name': 'Caution Deposit & Others', 'default_amount': Decimal('500.00')})
        self.stdout.write(self.style.SUCCESS("[OK] Fee categories configured"))

        # 6. Students
        students_data = [
            {
                'username': 'student1',
                'email': 'aarav.sharma@college.edu',
                'first_name': 'Aarav',
                'last_name': 'Sharma',
                'phone': '+91 91234 56781',
                'reg_number': 'REG-2026-001',
                'roll_number': 'CS-26-001',
                'gender': StudentProfile.Gender.MALE,
                'course': 'B.Tech Computer Science',
                'department': 'Computer Science & Engineering',
                'academic_year': '2nd Year',
                'parent_name': 'Vikas Sharma',
                'parent_phone': '+91 98111 00001',
                'emergency_contact': '+91 98111 00002',
                'address': 'Plot 42, Civil Lines, Jaipur, Rajasthan',
                'room': r101,
            },
            {
                'username': 'student2',
                'email': 'rohit.patel@college.edu',
                'first_name': 'Rohit',
                'last_name': 'Patel',
                'phone': '+91 91234 56782',
                'reg_number': 'REG-2026-002',
                'roll_number': 'CS-26-002',
                'gender': StudentProfile.Gender.MALE,
                'course': 'B.Tech Computer Science',
                'department': 'Computer Science & Engineering',
                'academic_year': '2nd Year',
                'parent_name': 'Mahesh Patel',
                'parent_phone': '+91 98111 00003',
                'emergency_contact': '+91 98111 00004',
                'address': 'B-14, Navrangpura, Ahmedabad, Gujarat',
                'room': r101,  # Roommate with student1
            },
            {
                'username': 'student3',
                'email': 'priya.singh@college.edu',
                'first_name': 'Priya',
                'last_name': 'Singh',
                'phone': '+91 91234 56783',
                'reg_number': 'REG-2026-003',
                'roll_number': 'EC-26-015',
                'gender': StudentProfile.Gender.FEMALE,
                'course': 'B.Tech Electronics & Comm.',
                'department': 'ECE',
                'academic_year': '3rd Year',
                'parent_name': 'Devendra Singh',
                'parent_phone': '+91 98111 00005',
                'emergency_contact': '+91 98111 00006',
                'address': 'Flat 302, Gomti Nagar, Lucknow, UP',
                'room': rg101,
            },
            {
                'username': 'student4',
                'email': 'ananya.iyer@college.edu',
                'first_name': 'Ananya',
                'last_name': 'Iyer',
                'phone': '+91 91234 56784',
                'reg_number': 'REG-2026-004',
                'roll_number': 'IT-26-022',
                'gender': StudentProfile.Gender.FEMALE,
                'course': 'B.Tech Information Technology',
                'department': 'IT',
                'academic_year': '1st Year',
                'parent_name': 'R. Iyer',
                'parent_phone': '+91 98111 00007',
                'emergency_contact': '+91 98111 00008',
                'address': '18, Anna Nagar, Chennai, Tamil Nadu',
                'room': rg101, # Roommate with student3
            },
            {
                'username': 'student5',
                'email': 'karan.mehta@college.edu',
                'first_name': 'Karan',
                'last_name': 'Mehta',
                'phone': '+91 91234 56785',
                'reg_number': 'REG-2026-005',
                'roll_number': 'ME-26-010',
                'gender': StudentProfile.Gender.MALE,
                'course': 'B.Tech Mechanical Engg',
                'department': 'Mechanical Engineering',
                'academic_year': '4th Year',
                'parent_name': 'Sanjay Mehta',
                'parent_phone': '+91 98111 00009',
                'emergency_contact': '+91 98111 00010',
                'address': 'Sector 14, Chandigarh',
                'room': r202,
            },
        ]

        created_students = []
        for sdata in students_data:
            s_user, _ = User.objects.get_or_create(
                username=sdata['username'],
                defaults={
                    'email': sdata['email'],
                    'first_name': sdata['first_name'],
                    'last_name': sdata['last_name'],
                    'role': User.Role.STUDENT,
                    'is_approved': True,
                    'is_active': True,
                    'phone': sdata['phone']
                }
            )
            s_user.set_password('StudentPassword123!')
            s_user.save()

            sp, _ = StudentProfile.objects.get_or_create(
                user=s_user,
                defaults={
                    'reg_number': sdata['reg_number'],
                    'roll_number': sdata['roll_number'],
                    'dob': timezone.now().date() - timezone.timedelta(days=7300),
                    'gender': sdata['gender'],
                    'course': sdata['course'],
                    'department': sdata['department'],
                    'academic_year': sdata['academic_year'],
                    'address': sdata['address'],
                    'parent_name': sdata['parent_name'],
                    'parent_phone': sdata['parent_phone'],
                    'emergency_contact': sdata['emergency_contact'],
                    'account_status': StudentProfile.AccountStatus.ACTIVE
                }
            )
            created_students.append((sp, sdata['room']))

            # Room Allocation
            target_room = sdata['room']
            if not RoomAllocation.objects.filter(student=sp, status='ACTIVE').exists():
                RoomAllocation.objects.create(
                    student=sp,
                    room=target_room,
                    allocation_date=timezone.now().date() - timezone.timedelta(days=90),
                    status=RoomAllocation.AllocationStatus.ACTIVE,
                    notes='Allocated at start of semester.',
                    allocated_by=admin_user
                )
                target_room.update_occupancy_status()

        # 1 Pending Student to test Admin Approval workflow
        pending_user, _ = User.objects.get_or_create(
            username='student_pending',
            defaults={
                'email': 'vikram.das@college.edu',
                'first_name': 'Vikram',
                'last_name': 'Das',
                'role': User.Role.STUDENT,
                'is_approved': False, # Pending admin approval!
                'is_active': True,
                'phone': '+91 91234 56799'
            }
        )
        pending_user.set_password('StudentPassword123!')
        pending_user.save()
        StudentProfile.objects.get_or_create(
            user=pending_user,
            defaults={
                'reg_number': 'REG-2026-099',
                'roll_number': 'CS-26-099',
                'dob': timezone.now().date() - timezone.timedelta(days=7000),
                'gender': StudentProfile.Gender.MALE,
                'course': 'MCA',
                'department': 'Computer Applications',
                'academic_year': '1st Year',
                'address': 'Bhubaneswar, Odisha',
                'parent_name': 'Ashok Das',
                'parent_phone': '+91 98111 99999',
                'emergency_contact': '+91 98111 99998',
                'account_status': StudentProfile.AccountStatus.PENDING
            }
        )
        self.stdout.write(self.style.SUCCESS("[OK] Students: student1 to student5, and student_pending / StudentPassword123!"))

        # 7. Fee Invoices & Payments
        curr_month = timezone.now().strftime('%Y-%m')
        prev_month = (timezone.now() - timezone.timedelta(days=30)).strftime('%Y-%m')

        for sp, room in created_students:
            # Previous month fee (Paid)
            fee_prev, _ = FeeRecord.objects.get_or_create(
                student=sp,
                billing_month=prev_month,
                category=fc_rent,
                defaults={
                    'title': f'{prev_month} Hostel Room Rent',
                    'total_amount': room.monthly_rent,
                    'paid_amount': room.monthly_rent,
                    'remaining_amount': Decimal('0.00'),
                    'due_date': timezone.now().date() - timezone.timedelta(days=35),
                    'status': FeeRecord.PaymentStatus.PAID
                }
            )
            # Create payment receipt for previous month
            if not fee_prev.payments.exists():
                Payment.objects.create(
                    fee_record=fee_prev,
                    amount=fee_prev.total_amount,
                    payment_date=timezone.now().date() - timezone.timedelta(days=40),
                    payment_method=Payment.PaymentMethod.UPI,
                    transaction_reference=f'UPI-SBI-{sp.reg_number}',
                    received_by=admin_user,
                    notes='Received full monthly rent.'
                )

            # Current month fee
            fee_curr, _ = FeeRecord.objects.get_or_create(
                student=sp,
                billing_month=curr_month,
                category=fc_rent,
                defaults={
                    'title': f'{curr_month} Hostel Room Rent',
                    'total_amount': room.monthly_rent,
                    'paid_amount': Decimal('0.00'),
                    'remaining_amount': room.monthly_rent,
                    'due_date': timezone.now().date() + timezone.timedelta(days=10),
                    'status': FeeRecord.PaymentStatus.PENDING
                }
            )

        # For student1, record partial payment for current month
        s1_sp = created_students[0][0]
        s1_curr_fee = FeeRecord.objects.filter(student=s1_sp, billing_month=curr_month).first()
        if s1_curr_fee and not s1_curr_fee.payments.exists():
            Payment.objects.create(
                fee_record=s1_curr_fee,
                amount=Decimal('2500.00'),
                payment_date=timezone.now().date() - timezone.timedelta(days=2),
                payment_method=Payment.PaymentMethod.UPI,
                transaction_reference='UPI-PAYTM-99238',
                received_by=admin_user,
                notes='Partial advance payment.'
            )

        # For student3, mess fee overdue
        s3_sp = created_students[2][0]
        FeeRecord.objects.get_or_create(
            student=s3_sp,
            billing_month=curr_month,
            category=fc_mess,
            defaults={
                'title': f'{curr_month} Dining Mess Charges',
                'total_amount': Decimal('3200.00'),
                'paid_amount': Decimal('0.00'),
                'remaining_amount': Decimal('3200.00'),
                'due_date': timezone.now().date() - timezone.timedelta(days=5),
                'status': FeeRecord.PaymentStatus.OVERDUE
            }
        )
        self.stdout.write(self.style.SUCCESS("[OK] Fee records and payments initialized"))

        # 8. Complaints
        s1_sp = created_students[0][0]
        c1, _ = Complaint.objects.get_or_create(
            student=s1_sp,
            title='Geyser heater in bathroom trip switch failing',
            defaults={
                'category': Complaint.Category.ELECTRICITY,
                'description': 'The water geyser in Room 101 trips the MCB circuit breaker after 5 minutes of heating. Please dispatch an electrician.',
                'status': Complaint.Status.IN_PROGRESS,
                'assigned_warden': WardenProfile.objects.first()
            }
        )
        if not c1.history.exists():
            ComplaintHistory.objects.create(
                complaint=c1,
                action_by=admin_user,
                status_from='SUBMITTED',
                status_to='IN_PROGRESS',
                remarks='Electrician scheduled for afternoon maintenance.'
            )

        s2_sp = created_students[1][0]
        c2, _ = Complaint.objects.get_or_create(
            student=s2_sp,
            title='Slow Wi-Fi connectivity in 1st floor wing',
            defaults={
                'category': Complaint.Category.INTERNET,
                'description': 'Wi-Fi speeds drop drastically after 8 PM, making it difficult to attend virtual lectures.',
                'status': Complaint.Status.SUBMITTED
            }
        )

        s3_sp = created_students[2][0]
        c3, _ = Complaint.objects.get_or_create(
            student=s3_sp,
            title='Water tap leaking in washbasin',
            defaults={
                'category': Complaint.Category.WATER_SUPPLY,
                'description': 'Washbasin tap in Room 101 GH-1 has a persistent drip.',
                'status': Complaint.Status.RESOLVED,
                'resolution_notes': 'Washer valve replaced by maintenance staff.',
                'resolved_at': timezone.now()
            }
        )
        self.stdout.write(self.style.SUCCESS("[OK] Complaints & audit history created"))

        # 9. Attendance
        for sp, _ in created_students:
            for day_offset in range(7):
                att_date = timezone.now().date() - timezone.timedelta(days=day_offset)
                Attendance.objects.get_or_create(
                    student=sp,
                    date=att_date,
                    defaults={
                        'status': Attendance.Status.PRESENT if (sp.id + day_offset) % 6 != 0 else Attendance.Status.ABSENT,
                        'remarks': 'Sick leave' if (sp.id + day_offset) % 6 == 0 else '',
                        'recorded_by': admin_user
                    }
                )
        self.stdout.write(self.style.SUCCESS("[OK] Daily attendance logs populated"))

        # 10. Notices
        Notice.objects.get_or_create(
            title='Hostel Gate Timing & Night Pass Guidelines',
            defaults={
                'content': 'All residents are hereby notified that hostel main gates will close strictly at 10:00 PM. Any late entry requires prior written approval from the Warden office. Breach of hostel curfew will attract strict disciplinary penalties.',
                'target_audience': Notice.Audience.ALL,
                'published_date': timezone.now().date() - timezone.timedelta(days=5),
                'is_published': True,
                'created_by': admin_user
            }
        )

        Notice.objects.get_or_create(
            title='Mess Menu Revision & Winter Term Dietary Feedback',
            defaults={
                'content': 'The Student Mess Committee has revised the weekly dinner menu to include warm soups and seasonal dishes. Students can submit dietary suggestions directly via the complaints / suggestion portal.',
                'target_audience': Notice.Audience.STUDENTS,
                'published_date': timezone.now().date() - timezone.timedelta(days=2),
                'is_published': True,
                'created_by': admin_user
            }
        )

        Notice.objects.get_or_create(
            title='Annual Fire Safety Drill & Electrical Inspection',
            defaults={
                'content': 'Mandatory fire evacuation drill will take place on Saturday at 11:00 AM across all hostel blocks. Please ensure electrical appliances (heaters/kettles) conform to hostel safety guidelines.',
                'target_audience': Notice.Audience.ALL,
                'published_date': timezone.now().date(),
                'is_published': True,
                'created_by': admin_user
            }
        )
        self.stdout.write(self.style.SUCCESS("[OK] Notice bulletins published"))

        # 11. Visitors
        Visitor.objects.get_or_create(
            visitor_name='Sunil Sharma',
            phone_number='+91 98765 44444',
            student=s1_sp,
            defaults={
                'relationship': 'Father',
                'purpose': 'Family visit & handing over study materials',
                'id_proof_type': 'Aadhaar Card',
                'id_proof_number': 'XXXX-XXXX-8921',
                'address': 'Jaipur, Rajasthan',
                'entry_time': timezone.now() - timezone.timedelta(hours=1),
                'exit_time': None, # Still inside
                'recorded_by': admin_user
            }
        )

        Visitor.objects.get_or_create(
            visitor_name='Ramesh Patel',
            phone_number='+91 98765 55555',
            student=created_students[1][0],
            defaults={
                'relationship': 'Uncle',
                'purpose': 'Medical checkup pickup',
                'id_proof_type': 'Driving License',
                'id_proof_number': 'DL-GJ-2019-1234',
                'address': 'Ahmedabad',
                'entry_time': timezone.now() - timezone.timedelta(hours=4),
                'exit_time': timezone.now() - timezone.timedelta(hours=2), # Exited
                'recorded_by': admin_user
            }
        )
        self.stdout.write(self.style.SUCCESS("[OK] Visitors checked in & logged"))

        self.stdout.write(self.style.SUCCESS("\n========================================================"))
        self.stdout.write(self.style.SUCCESS("SUCCESS: HOSTEL MANAGEMENT DATABASE FULLY INITIALIZED!"))
        self.stdout.write(self.style.SUCCESS("========================================================"))
