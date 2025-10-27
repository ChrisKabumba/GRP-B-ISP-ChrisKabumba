// ====== Main JavaScript for Interactivity ======

// Flash messages auto-dismiss
document.addEventListener("DOMContentLoaded", () => {
    const alerts = document.querySelectorAll(".alert");
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.classList.add("fade");
            setTimeout(() => alert.remove(), 500);
        }, 4000);
    });
});

// Confirm logout
function confirmLogout(event) {
    if (!confirm("Are you sure you want to log out?")) {
        event.preventDefault();
    }
}

// Animate form submissions (loading effect)
const forms = document.querySelectorAll("form");
forms.forEach(form => {
    form.addEventListener("submit", () => {
        const btn = form.querySelector("button[type='submit']");
        if (btn) {
            btn.innerHTML = "Processing...";
            btn.disabled = true;
        }
    });
});