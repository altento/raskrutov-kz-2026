/**
 * Raskrutov homepage clean — menu, modals, phone mask.
 * Lead submit handled solely by lead-forms.js.
 */
(function () {
  "use strict";

  var doc = document;
  var body = doc.body;
  if (!body || !body.classList.contains("rk-clean")) return;

  var lastFocus = null;
  var openModalId = null;

  function $(sel, root) {
    return (root || doc).querySelector(sel);
  }

  function $$(sel, root) {
    return Array.prototype.slice.call((root || doc).querySelectorAll(sel));
  }

  /* ---------- Mobile menu ---------- */
  function initMenu() {
    var burger = $("[data-rk-menu-toggle]");
    var panel = $("[data-rk-mobile-nav]");
    if (!burger || !panel) return;

    function setOpen(open) {
      burger.setAttribute("aria-expanded", open ? "true" : "false");
      panel.classList.toggle("is-open", open);
      panel.hidden = !open;
      body.classList.toggle("rk-menu-open", open);
      if (open) {
        var first = panel.querySelector("a");
        if (first) first.focus();
      }
    }

    setOpen(false);

    burger.addEventListener("click", function () {
      var open = burger.getAttribute("aria-expanded") !== "true";
      setOpen(open);
    });

    panel.addEventListener("click", function (e) {
      var a = e.target.closest("a");
      if (a) setOpen(false);
    });

    doc.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && burger.getAttribute("aria-expanded") === "true") {
        setOpen(false);
        burger.focus();
      }
    });
  }

  /* ---------- Modals ---------- */
  function getModal(id) {
    return doc.getElementById(id);
  }

  function trapFocus(modal, e) {
    if (e.key !== "Tab") return;
    var focusables = $$(
      'a[href], button:not([disabled]), input:not([disabled]), textarea:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])',
      modal
    ).filter(function (el) {
      return !el.closest("[hidden]") && el.offsetParent !== null;
    });
    if (!focusables.length) return;
    var first = focusables[0];
    var last = focusables[focusables.length - 1];
    if (e.shiftKey && doc.activeElement === first) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && doc.activeElement === last) {
      e.preventDefault();
      first.focus();
    }
  }

  function openModal(id, trigger) {
    var modal = getModal(id);
    if (!modal) return;
    lastFocus = trigger || doc.activeElement;
    openModalId = id;
    modal.hidden = false;
    body.classList.add("rk-modal-open");
    var closeBtn = $("[data-rk-modal-close]", modal);
    var focusTarget =
      modal.querySelector("input, textarea, button.rk-btn") || closeBtn || modal;
    requestAnimationFrame(function () {
      focusTarget.focus();
    });
  }

  function closeModal(id) {
    var modal = getModal(id || openModalId);
    if (!modal || modal.hidden) return;
    modal.hidden = true;
    if (!$$(".rk-modal:not([hidden])").length) {
      body.classList.remove("rk-modal-open");
    }
    openModalId = null;
    if (lastFocus && typeof lastFocus.focus === "function") {
      lastFocus.focus();
    }
    lastFocus = null;
  }

  function initModals() {
    doc.addEventListener("click", function (e) {
      var switchBtn = e.target.closest("[data-rk-switch-modal]");
      if (switchBtn) {
        e.preventDefault();
        var nextId = switchBtn.getAttribute("data-rk-switch-modal");
        var current = switchBtn.closest(".rk-modal");
        var restore = lastFocus;
        if (current) {
          current.hidden = true;
          openModalId = null;
        }
        openModal(nextId, restore || switchBtn);
        return;
      }
      var openBtn = e.target.closest("[data-rk-open-modal]");
      if (openBtn) {
        e.preventDefault();
        openModal(openBtn.getAttribute("data-rk-open-modal"), openBtn);
        return;
      }
      var closeBtn = e.target.closest("[data-rk-modal-close]");
      if (closeBtn) {
        e.preventDefault();
        var m = closeBtn.closest(".rk-modal");
        closeModal(m && m.id);
        return;
      }
      if (e.target.classList && e.target.classList.contains("rk-modal__backdrop")) {
        var modal = e.target.closest(".rk-modal");
        closeModal(modal && modal.id);
      }
    });

    doc.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && openModalId) {
        closeModal(openModalId);
        return;
      }
      if (e.key === "Tab" && openModalId) {
        var modal = getModal(openModalId);
        if (modal && !modal.hidden) trapFocus(modal, e);
      }
    });
  }

  /* ---------- Phone mask +7 (___) ___ __ __ ---------- */
  function digitsOnly(v) {
    return String(v || "").replace(/\D+/g, "");
  }

  function formatPhone(raw) {
    var d = digitsOnly(raw);
    if (d.charAt(0) === "8") d = "7" + d.slice(1);
    if (d.charAt(0) !== "7") d = "7" + d;
    d = d.slice(0, 11);
    var out = "+7";
    if (d.length > 1) out += " (" + d.slice(1, Math.min(4, d.length));
    if (d.length >= 4) out += ")";
    if (d.length > 4) out += " " + d.slice(4, Math.min(7, d.length));
    if (d.length > 7) out += " " + d.slice(7, Math.min(9, d.length));
    if (d.length > 9) out += " " + d.slice(9, 11);
    return out;
  }

  function initPhoneMask() {
    $$('input[type="tel"][data-rk-phone-mask]').forEach(function (input) {
      input.addEventListener("focus", function () {
        if (!digitsOnly(input.value)) input.value = "+7 (";
      });
      input.addEventListener("input", function () {
        var start = input.selectionStart;
        var before = input.value.length;
        input.value = formatPhone(input.value);
        var after = input.value.length;
        if (typeof start === "number") {
          var pos = Math.max(0, start + (after - before));
          try {
            input.setSelectionRange(pos, pos);
          } catch (err) {}
        }
      });
      input.addEventListener("blur", function () {
        if (digitsOnly(input.value).length <= 1) input.value = "";
      });
    });
  }

  /* ---------- Scroll top + soc widget ---------- */
  function initScrollTop() {
    var btn = $("[data-rk-scroll-top]");
    if (!btn) return;

    var showAt = 400;

    function toggle() {
      btn.classList.toggle("rk-scroll-top--visible", window.scrollY > showAt);
    }

    var ticking = false;
    function onScroll() {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(function () {
        ticking = false;
        toggle();
      });
    }

    window.addEventListener("scroll", onScroll, { passive: true });
    toggle();

    btn.addEventListener("click", function () {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  function initSocWidget() {
    var widget = $(".rk-soc-widget");
    var toggle = $("[data-rk-soc-toggle]");
    if (!widget || !toggle) return;

    toggle.addEventListener("click", function (e) {
      e.stopPropagation();
      var open = widget.classList.toggle("rk-soc-widget--opened");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });

    doc.addEventListener("click", function (e) {
      if (!widget.contains(e.target)) {
        widget.classList.remove("rk-soc-widget--opened");
        toggle.setAttribute("aria-expanded", "false");
      }
    });
  }

  /* ---------- Yandex map (lazy iframe) ---------- */
  function initMap() {
    var el = $("[data-rk-map]");
    if (!el || el.getAttribute("data-ready") === "1") return;

    function mount() {
      if (el.getAttribute("data-ready") === "1") return;
      el.setAttribute("data-ready", "1");
      var lat = el.getAttribute("data-lat") || "54.8746";
      var lon = el.getAttribute("data-lon") || "69.135701";
      var zoom = el.getAttribute("data-zoom") || "16";
      var iframe = doc.createElement("iframe");
      iframe.src =
        "https://yandex.ru/map-widget/v1/?ll=" +
        encodeURIComponent(lon + "," + lat) +
        "&z=" +
        zoom +
        "&pt=" +
        encodeURIComponent(lon + "," + lat + ",pm2rdm") +
        "&l=map";
      iframe.title = el.getAttribute("aria-label") || "Карта офиса Raskrutov";
      iframe.loading = "lazy";
      iframe.setAttribute("allowfullscreen", "");
      iframe.referrerPolicy = "no-referrer-when-downgrade";
      el.appendChild(iframe);
    }

    if ("IntersectionObserver" in window) {
      var io = new IntersectionObserver(
        function (entries) {
          if (
            entries.some(function (entry) {
              return entry.isIntersecting;
            })
          ) {
            io.disconnect();
            mount();
          }
        },
        { rootMargin: "240px 0px" }
      );
      io.observe(el);
    } else {
      mount();
    }
  }

  /* ---------- Init ---------- */
  function init() {
    initMenu();
    initModals();
    initPhoneMask();
    initScrollTop();
    initSocWidget();
    initMap();
  }

  if (doc.readyState === "loading") {
    doc.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
