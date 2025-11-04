// ===========================
// Main JavaScript for Interactivity
// ===========================

document.addEventListener("DOMContentLoaded", () => {

  /* ---------------------------
     1. AUTO-DISMISS FLASH MESSAGES
     --------------------------- */
  const alerts = document.querySelectorAll(".alert");
  alerts.forEach(alert => {
    setTimeout(() => {
      alert.classList.add("fade-out");
      setTimeout(() => alert.remove(), 500);
    }, 4000);
  });

  /* ---------------------------
     2. CONFIRM LOGOUT
     --------------------------- */
  const logoutLinks = document.querySelectorAll(".logout-link");
  logoutLinks.forEach(link => {
    link.addEventListener("click", e => {
      if (!confirm("Are you sure you want to log out?")) {
        e.preventDefault();
      }
    });
  });

  /* ---------------------------
     3. CONFIRM DELETE ACTIONS
     --------------------------- */
  const deleteForms = document.querySelectorAll("form.delete-form");
  deleteForms.forEach(form => {
    form.addEventListener("submit", e => {
      if (!confirm("Are you sure you want to delete this item?")) {
        e.preventDefault();
      }
    });
  });

  /* ---------------------------
     4. FORM SUBMISSION LOADING EFFECT
     --------------------------- */
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

  /* ---------------------------
     5. FADE-IN EFFECT ON LOAD
     --------------------------- */
  const fadeElements = document.querySelectorAll(".fade-in");
  fadeElements.forEach(el => {
    el.style.opacity = 0;
    setTimeout(() => {
      el.style.transition = "opacity 0.8s ease-in";
      el.style.opacity = 1;
    }, 100);
  });

  /* ---------------------------
     6. TOOLTIP INITIALIZATION (Bootstrap 5)
     --------------------------- */
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(el => new bootstrap.Tooltip(el));

  /* ---------------------------
     7. SMOOTH SCROLL TO TOP
     --------------------------- */
  const toTopBtn = document.querySelector("#toTopBtn");
  if (toTopBtn) {
    window.addEventListener("scroll", () => {
      toTopBtn.style.display = window.scrollY > 200 ? "block" : "none";
    });

    toTopBtn.addEventListener("click", () => {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }
});