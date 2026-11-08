from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils import timezone
from accounts.models import User
from students.models import StudentProfile
from wardens.models import WardenProfile
from hostels.models import Hostel, Floor
from rooms.models import Room
from allocations.models import RoomAllocation
from fees.models import FeeCategory, FeeRecord, Payment
from attendance.models import Attendance
from complaints.models import Complaint

class HostelManagementSystemTests(TestCase):
    def setUp(self):
        # 1. Super Admin
        self.admin_user = User.objects.create_superuser(
            username='admin_test',
            email='admin@test.com',
            password='TestPassword123!',
            role=User.Role.SUPER_ADMIN
        )

        # 2. Hostel & Room
        self.hostel = Hostel.objects.create(
            name='Test Boys Hostel',
            code='TBH-1',
            gender_type=Hostel.GenderType.BOYS
        )
        self.floor = Floor.objects.create(
            hostel=self.hostel,
            floor_number=1,
            floor_name='First Floor'
        )
        self.room = Room.objects.create(
            hostel=self.hostel,
            floor=self.floor,
            room_number='101',
            room_type=Room.RoomType.DOUBLE,
            capacity=2,
            monthly_rent=Decimal('5000.00'),
            room_status=Room.RoomStatus.AVAILABLE
        )

        # 3. Students
        self.student1_user = User.objects.create_user(
            username='student1_test',
            email='student1@test.com',
            password='TestPassword123!',
            role=User.Role.STUDENT,
            is_approved=True
        )
        self.student1 = StudentProfile.objects.create(
            user=self.student1_user,
            reg_number='REG-TEST-001',
            course='B.Tech CSE',
            department='CSE',
            account_status=StudentProfile.AccountStatus.ACTIVE
        )

        self.student2_user = User.objects.create_user(
            username='student2_test',
            email='student2@test.com',
            password='TestPassword123!',
            role=User.Role.STUDENT,
            is_approved=True
        )
        self.student2 = StudentProfile.objects.create(
            user=self.student2_user,
            reg_number='REG-TEST-002',
            course='B.Tech CSE',
            department='CSE',
            account_status=StudentProfile.AccountStatus.ACTIVE
        )

        self.student3_user = User.objects.create_user(
            username='student3_test',
            email='student3@test.com',
            password='TestPassword123!',
            role=User.Role.STUDENT,
            is_approved=True
        )
        self.student3 = StudentProfile.objects.create(
            user=self.student3_user,
            reg_number='REG-TEST-003',
            course='B.Tech CSE',
            department='CSE',
            account_status=StudentProfile.AccountStatus.ACTIVE
        )

    def test_room_allocation_and_occupancy_update(self):
        """Test allocating bed updates occupancy and room status."""
        self.assertEqual(self.room.current_occupancy, 0)
        self.assertEqual(self.room.available_beds, 2)
        self.assertEqual(self.room.room_status, Room.RoomStatus.AVAILABLE)

        # Allocate student 1
        alloc1 = RoomAllocation.objects.create(
            student=self.student1,
            room=self.room,
            status=RoomAllocation.AllocationStatus.ACTIVE
        )
        self.room.refresh_from_db()
        self.assertEqual(self.room.current_occupancy, 1)
        self.assertEqual(self.room.available_beds, 1)
        self.assertEqual(self.room.room_status, Room.RoomStatus.PARTIALLY_OCCUPIED)

        # Allocate student 2 (room becomes FULL)
        alloc2 = RoomAllocation.objects.create(
            student=self.student2,
            room=self.room,
            status=RoomAllocation.AllocationStatus.ACTIVE
        )
        self.room.refresh_from_db()
        self.assertEqual(self.room.current_occupancy, 2)
        self.assertEqual(self.room.available_beds, 0)
        self.assertEqual(self.room.room_status, Room.RoomStatus.FULL)

        # Over-allocation test (Capacity is 2, allocating 3rd student must fail)
        with self.assertRaises(ValidationError):
            alloc3 = RoomAllocation(
                student=self.student3,
                room=self.room,
                status=RoomAllocation.AllocationStatus.ACTIVE
            )
            alloc3.clean()

    def test_prevent_duplicate_active_allocation(self):
        """Test student cannot have two active room allocations."""
        RoomAllocation.objects.create(
            student=self.student1,
            room=self.room,
            status=RoomAllocation.AllocationStatus.ACTIVE
        )
        # Attempting second active allocation for student1 must raise ValidationError
        room2 = Room.objects.create(
            hostel=self.hostel,
            floor=self.floor,
            room_number='102',
            capacity=1,
            monthly_rent=Decimal('6000.00')
        )
        with self.assertRaises(ValidationError):
            second_alloc = RoomAllocation(
                student=self.student1,
                room=room2,
                status=RoomAllocation.AllocationStatus.ACTIVE
            )
            second_alloc.clean()

    def test_room_vacate(self):
        """Test vacating room increases available beds and sets status."""
        alloc = RoomAllocation.objects.create(
            student=self.student1,
            room=self.room,
            status=RoomAllocation.AllocationStatus.ACTIVE
        )
        self.room.refresh_from_db()
        self.assertEqual(self.room.current_occupancy, 1)

        # Vacate
        alloc.vacate(notes="Semester ended")
        self.room.refresh_from_db()
        self.assertEqual(alloc.status, RoomAllocation.AllocationStatus.VACATED)
        self.assertEqual(self.room.current_occupancy, 0)
        self.assertEqual(self.room.room_status, Room.RoomStatus.AVAILABLE)

    def test_fee_calculation_and_payment(self):
        """Test fee generation, partial payment, and balance recalculation."""
        cat = FeeCategory.objects.create(name='Test Rent', code='TEST_RENT', default_amount=Decimal('5000.00'))
        fee = FeeRecord.objects.create(
            student=self.student1,
            category=cat,
            title='November 2026 Rent',
            billing_month='2026-11',
            total_amount=Decimal('5000.00'),
            remaining_amount=Decimal('5000.00'),
            due_date=timezone.now().date() + timezone.timedelta(days=10),
            status=FeeRecord.PaymentStatus.PENDING
        )
        self.assertEqual(fee.remaining_amount, Decimal('5000.00'))

        # Make partial payment of 2000
        Payment.objects.create(
            fee_record=fee,
            amount=Decimal('2000.00'),
            payment_method=Payment.PaymentMethod.UPI,
            received_by=self.admin_user
        )
        fee.refresh_from_db()
        self.assertEqual(fee.paid_amount, Decimal('2000.00'))
        self.assertEqual(fee.remaining_amount, Decimal('3000.00'))
        self.assertEqual(fee.status, FeeRecord.PaymentStatus.PARTIALLY_PAID)

        # Clear remaining 3000
        Payment.objects.create(
            fee_record=fee,
            amount=Decimal('3000.00'),
            payment_method=Payment.PaymentMethod.CASH,
            received_by=self.admin_user
        )
        fee.refresh_from_db()
        self.assertEqual(fee.paid_amount, Decimal('5000.00'))
        self.assertEqual(fee.remaining_amount, Decimal('0.00'))
        self.assertEqual(fee.status, FeeRecord.PaymentStatus.PAID)

    def test_attendance_unique_per_date(self):
        """Test preventing duplicate attendance for same student on same date."""
        today = timezone.now().date()
        Attendance.objects.create(
            student=self.student1,
            date=today,
            status=Attendance.Status.PRESENT,
            recorded_by=self.admin_user
        )
        # Creating duplicate record must raise integrity error
        with self.assertRaises(Exception):
            Attendance.objects.create(
                student=self.student1,
                date=today,
                status=Attendance.Status.ABSENT,
                recorded_by=self.admin_user
            )

    def test_role_based_access_restriction(self):
        """Test student cannot access admin or warden dashboards."""
        self.client.login(username='student1_test', password='TestPassword123!')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 302) # Redirected away with access denied
