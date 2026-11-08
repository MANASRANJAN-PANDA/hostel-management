// HostelPulse Main JS
document.addEventListener('DOMContentLoaded', function () {
  // 1. Mobile Sidebar Toggle
  const toggleBtn = document.getElementById('sidebar-toggle-btn');
  const sidebar = document.querySelector('.app-sidebar');

  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      sidebar.classList.toggle('show');
    });

    document.addEventListener('click', function (e) {
      if (window.innerWidth < 992 && sidebar.classList.contains('show')) {
        if (!sidebar.contains(e.target) && e.target !== toggleBtn) {
          sidebar.classList.remove('show');
        }
      }
    });
  }

  // 2. Password Show / Hide Toggle
  const togglePasswordBtns = document.querySelectorAll('.toggle-password-visibility');
  togglePasswordBtns.forEach(btn => {
    btn.addEventListener('click', function () {
      const targetId = this.getAttribute('data-target');
      const input = document.getElementById(targetId);
      if (input) {
        if (input.type === 'password') {
          input.type = 'text';
          this.innerHTML = '<i class="fa-solid fa-eye-slash"></i>';
        } else {
          input.type = 'password';
          this.innerHTML = '<i class="fa-solid fa-eye"></i>';
        }
      }
    });
  });

  // 3. Dynamic Floor Loading when Hostel changes in forms
  const hostelSelect = document.getElementById('id_hostel');
  const floorSelect = document.getElementById('id_floor');

  if (hostelSelect && floorSelect) {
    hostelSelect.addEventListener('change', function () {
      const hostelId = this.value;
      if (!hostelId) {
        floorSelect.innerHTML = '<option value="">Select floor...</option>';
        return;
      }
      fetch(`/rooms/ajax/load-floors/?hostel_id=${hostelId}`)
        .then(res => res.json())
        .then(data => {
          let options = '<option value="">Select floor...</option>';
          data.forEach(floor => {
            options += `<option value="${floor.id}">${floor.floor_name} (Floor ${floor.floor_number})</option>`;
          });
          floorSelect.innerHTML = options;
        })
        .catch(err => console.error("Error loading floors:", err));
    });
  }

  // 4. Auto dismiss alerts after 5 seconds
  const autoAlerts = document.querySelectorAll('.alert-dismissible');
  autoAlerts.forEach(alert => {
    setTimeout(() => {
      try {
        const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
        if (bsAlert) bsAlert.close();
      } catch (e) {
        alert.style.display = 'none';
      }
    }, 5000);
  });
});
