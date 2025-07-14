  window.onload = function() {
    const params = new URLSearchParams(window.location.search);
    if (params.get("success") === "true") {
      const alertBox = document.getElementById("successAlert");
      alertBox.classList.remove("d-none");
      setTimeout(() => {
        alertBox.classList.add("d-none");
      }, 3000);
    }
  }
  // JS gán giá trị cho modal khi nhấn sửa
document.querySelectorAll('.btn-sua-tour').forEach(button => {
    button.addEventListener('click', function () {
        const tour = JSON.parse(this.dataset.tour);

        document.getElementById('tourIdInput').value = tour.id;
        document.getElementById('tourNameInput').value = tour.name;
        document.getElementById('tourCodeInput').value = tour.code;
        document.getElementById('tourPriceInput').value = tour.price;
        document.getElementById('tourDurationInput').value = tour.duration_days;
        document.getElementById('tourDescribeInput').value = tour.describe;
        
        // ✅ Hiển thị ngày bắt đầu nếu có
        if (tour.start_date) {
            document.getElementById('tourStartInput').value = tour.start_date;
        }

        const modal = new bootstrap.Modal(document.getElementById('tourModal'));
        modal.show();
    });
});
