(function () {
  "use strict";

  var toggle = document.querySelector("[data-menu-toggle]");
  var navigation = document.querySelector("[data-site-nav]");
  var scrollTopButton = document.querySelector("[data-scroll-top]");

  function closeMenu() {
    if (!toggle || !navigation) return;
    toggle.setAttribute("aria-expanded", "false");
    toggle.setAttribute("aria-label", "Открыть меню");
    navigation.classList.remove("is-open");
    document.body.classList.remove("nav-open");
  }

  if (toggle && navigation) {
    toggle.addEventListener("click", function () {
      var isOpen = toggle.getAttribute("aria-expanded") === "true";
      toggle.setAttribute("aria-expanded", String(!isOpen));
      toggle.setAttribute("aria-label", isOpen ? "Открыть меню" : "Закрыть меню");
      navigation.classList.toggle("is-open", !isOpen);
      document.body.classList.toggle("nav-open", !isOpen);
    });

    navigation.addEventListener("click", function (event) {
      if (event.target.closest("a")) closeMenu();
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") {
        closeMenu();
        toggle.focus();
      }
    });

    window.addEventListener("resize", function () {
      if (window.innerWidth > 980) closeMenu();
    });
  }

  if (scrollTopButton) {
    function updateScrollTopButton() {
      scrollTopButton.classList.toggle("is-visible", window.scrollY > 650);
    }

    updateScrollTopButton();
    window.addEventListener("scroll", updateScrollTopButton, { passive: true });
    scrollTopButton.addEventListener("click", function () {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  document.addEventListener("click", function (event) {
    var link = event.target.closest("a[href]");
    if (!link) return;

    var href = link.getAttribute("href") || "";
    var isTrackedAction = href.indexOf("tel:") === 0 ||
      href.indexOf("wa.me/") !== -1 ||
      href.indexOf("franshiza2024.kz") !== -1;

    if (!isTrackedAction) return;

    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({
      event: "case_cta_click",
      case_name: "turan_agency",
      link_url: href,
      link_text: (link.textContent || "").trim().slice(0, 100)
    });
  });
})();
