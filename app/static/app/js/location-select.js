<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>

  const api = "https://provinces.open-api.vn/api/";

  $(document).ready(function () {
    // Load danh sách tỉnh
    $.get(api + "?depth=1", function (data) {
      data.forEach(p => {
        $("#province").append(`<option value="${p.code}">${p.name}</option>`);
      });
    });

    // Khi chọn tỉnh → load huyện
    $("#province").on("change", function () {
      let provinceCode = $(this).val();
      $("#district").prop("disabled", false).empty().append('<option value="">-- Chọn quận/huyện --</option>');
      $("#ward").prop("disabled", true).empty().append('<option value="">-- Chọn xã/phường --</option>');

      if (provinceCode) {
        $.get(api + `p/${provinceCode}?depth=2`, function (data) {
          data.districts.forEach(d => {
            $("#district").append(`<option value="${d.code}">${d.name}</option>`);
          });
        });
      }
    });

    // Khi chọn huyện → load xã
    $("#district").on("change", function () {
      let districtCode = $(this).val();
      $("#ward").prop("disabled", false).empty().append('<option value="">-- Chọn xã/phường --</option>');

      if (districtCode) {
        $.get(api + `d/${districtCode}?depth=2`, function (data) {
          data.wards.forEach(w => {
            $("#ward").append(`<option value="${w.name}">${w.name}</option>`);
          });
        });
      }
    });
  });

