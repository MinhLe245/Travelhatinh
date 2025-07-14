document.addEventListener("DOMContentLoaded", function() {
  const buttons = document.querySelectorAll(".add-to-cart-btn");
  const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

  buttons.forEach(button => {
    button.addEventListener("click", function(e) {
      e.preventDefault();
      const tourId = this.dataset.tourId;

      fetch("/api/add-to-cart/", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
          "X-CSRFToken": csrfToken
        },
        body: `tour_id=${tourId}`
      })
      .then(response => response.text())
      .then(text => {
        try {
          const data = JSON.parse(text);
          if (data.success) {
            showToast(data.message || "Đã thêm tour vào giỏ hàng!");
          } else {
            alert(data.error || "Có lỗi xảy ra!");
          }
        } catch (error) {
          console.error("Lỗi phân tích JSON:", error);
          console.warn("Phản hồi trả về:", text);

          // Nếu trả về là HTML, có thể do chưa login
          if (text.includes("<!DOCTYPE html>") && text.includes("login")) {
            alert("Bạn cần đăng nhập để thêm tour.");
            window.location.href = "/login/?next=" + window.location.pathname;
          }
        }
      })
      .catch(error => {
        console.error("Lỗi kết nối:", error);
        alert("Không thể kết nối đến server.");
      });
    });
  });

  function showToast(message) {
    const toast = document.createElement("div");
    toast.innerText = message;
    toast.style.position = "fixed";
    toast.style.bottom = "20px";
    toast.style.right = "20px";
    toast.style.background = "#198754";
    toast.style.color = "#fff";
    toast.style.padding = "10px 20px";
    toast.style.borderRadius = "8px";
    toast.style.zIndex = 10000;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 2500);
  }
});
