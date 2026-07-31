/**
 * Raskrutov unified lead forms → Supabase Edge Function.
 * Auto-binds forms with [data-lead-form]. Safe for static multi-page HTML.
 */
(function () {
  "use strict";

  if (typeof window === "undefined" || typeof document === "undefined") return;

  // If a GitHub Pages build was uploaded to Plesk, links become /raskrutov-kz-2026/...
  // Strip that base on domain-root hosts so «Главная» and menu work.
  var GH_BASE = "/raskrutov-kz-2026";
  function shouldStripGhBase() {
    try {
      var h = window.location.hostname || "";
      return !/github\.io$/i.test(h);
    } catch (e) {
      return false;
    }
  }
  function stripGhPath(val) {
    if (!val || typeof val !== "string") return val;
    if (val === GH_BASE || val === GH_BASE + "/") return "/";
    if (val.indexOf(GH_BASE + "/") === 0) return val.slice(GH_BASE.length);
    return val;
  }
  function stripGhBaseFromDom(root) {
    if (!shouldStripGhBase()) return;
    var attrs = ["href", "src", "action", "data-page-link", "poster"];
    var nodes = (root || document).querySelectorAll(
      "[href],[src],[action],[data-page-link],[poster]"
    );
    for (var i = 0; i < nodes.length; i++) {
      var el = nodes[i];
      for (var j = 0; j < attrs.length; j++) {
        var a = attrs[j];
        if (!el.hasAttribute(a)) continue;
        var cur = el.getAttribute(a);
        var next = stripGhPath(cur);
        if (next !== cur) el.setAttribute(a, next);
      }
    }
  }
  if (shouldStripGhBase()) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", function () {
        stripGhBaseFromDom(document);
      });
    } else {
      stripGhBaseFromDom(document);
    }
  }

  var ENDPOINT =
    "https://rslemacnycrxzdatwarv.supabase.co/functions/v1/submit-lead";
  var UTM_KEYS = [
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_content",
    "utm_term",
  ];
  var UTM_STORAGE_KEY = "raskrutov_utm_v1";
  var STANDARD_FIELDS = [
    "name",
    "phone",
    "email",
    "message",
    "service",
    "company",
    "budget",
    "website",
  ];

  /** Cryptic Mottor field names → logical names (sitewide). */
  var FIELD_ALIASES = {
    // contacts msf1991300
    omnh9JD: "name",
    F83cj9B: "phone",
    // popup msf1974746
    fqH8tlT: "name",
    DfDdcMf: "phone",
    "JU4d-Mu": "email",
    "G-CLHVX": "message",
    // digital audit msf2015027
    "v-7m62z": "name",
    snkJsue: "phone",
    qhnx4Bp: "email",
    vuSJRe1: "message",
    // digital consult msf2015014
    r2a5M_k: "name",
    SjK4AaJ: "phone",
    LrPOUoh: "email",
    BsiV9mz: "message",
    // ads budget msf2014788
    FS60l4s: "name",
    j_NWtdo: "phone",
    MhdwgML: "email",
    RK1jE8T: "message",
    // ads strategy msf2014786
    MKmoGWf: "name",
    Dn3qEvi: "phone",
    VZBYjod: "email",
    WOwv7gR: "message",
  };

  function trim(v) {
    return String(v == null ? "" : v).trim();
  }

  function readUtmsFromUrl() {
    var out = {};
    var params;
    try {
      params = new URLSearchParams(window.location.search || "");
    } catch (e) {
      return out;
    }
    UTM_KEYS.forEach(function (k) {
      var v = params.get(k);
      if (v) out[k] = v;
    });
    return out;
  }

  function saveUtms(utms) {
    if (!utms || !Object.keys(utms).length) return;
    try {
      var prev = {};
      try {
        prev = JSON.parse(sessionStorage.getItem(UTM_STORAGE_KEY) || "{}") || {};
      } catch (e) {}
      var next = Object.assign({}, prev, utms);
      sessionStorage.setItem(UTM_STORAGE_KEY, JSON.stringify(next));
    } catch (e) {}
  }

  function loadStoredUtms() {
    try {
      return JSON.parse(sessionStorage.getItem(UTM_STORAGE_KEY) || "{}") || {};
    } catch (e) {
      return {};
    }
  }

  function resolveUtms() {
    var fromUrl = readUtmsFromUrl();
    if (Object.keys(fromUrl).length) {
      saveUtms(fromUrl);
      var stored = loadStoredUtms();
      return {
        utm_source: fromUrl.utm_source || stored.utm_source || "",
        utm_medium: fromUrl.utm_medium || stored.utm_medium || "",
        utm_campaign: fromUrl.utm_campaign || stored.utm_campaign || "",
        utm_content: fromUrl.utm_content || stored.utm_content || "",
        utm_term: fromUrl.utm_term || stored.utm_term || "",
      };
    }
    var s = loadStoredUtms();
    return {
      utm_source: s.utm_source || "",
      utm_medium: s.utm_medium || "",
      utm_campaign: s.utm_campaign || "",
      utm_content: s.utm_content || "",
      utm_term: s.utm_term || "",
    };
  }

  // Capture UTM on first paint
  saveUtms(readUtmsFromUrl());

  function logicalNameForControl(el) {
    if (!el) return "";
    var n = el.getAttribute("name") || "";
    if (STANDARD_FIELDS.indexOf(n) !== -1) return n;
    if (FIELD_ALIASES[n]) return FIELD_ALIASES[n];
    var wrap = el.closest && el.closest(".msf-input__wrapper");
    if (wrap) {
      var t = wrap.getAttribute("type");
      if (t === "name" || t === "phone" || t === "email") return t;
      if (t === "textarea" || el.tagName === "TEXTAREA") return "message";
    }
    if (el.tagName === "TEXTAREA") return "message";
    var typ = (el.getAttribute("type") || "").toLowerCase();
    if (typ === "tel") return "phone";
    if (typ === "email") return "email";
    return n;
  }

  function collectFields(form) {
    var data = {};
    var controls = form.querySelectorAll("input, textarea, select");
    for (var i = 0; i < controls.length; i++) {
      var el = controls[i];
      var typ = (el.getAttribute("type") || "").toLowerCase();
      if (typ === "submit" || typ === "button" || typ === "image" || typ === "file")
        continue;
      if (el.name === "ms_meta" || el.name === "regulation") continue;
      var key = logicalNameForControl(el);
      if (!key) continue;
      // honeypot website always from name=website
      if (el.name === "website") key = "website";
      var val = trim(el.value);
      if (key in data && !val) continue;
      data[key] = val;
    }
    return data;
  }

  function buildMessage(fields) {
    var parts = [];
    if (fields.service) parts.push("Услуга: " + fields.service);
    if (fields.company) parts.push("Компания: " + fields.company);
    if (fields.budget) parts.push("Бюджет: " + fields.budget);
    var msg = fields.message || "";
    if (parts.length) {
      return parts.join("\n") + (msg ? "\n\nСообщение клиента: " + msg : "");
    }
    return msg;
  }

  function ensureStatusEl(form) {
    var el = form.querySelector("[data-form-status]");
    if (el) return el;
    el = document.createElement("div");
    el.setAttribute("data-form-status", "");
    el.setAttribute("aria-live", "polite");
    el.className = "lead-form-status";
    var btnWrap =
      form.querySelector(".msf-submit, .user_form_submit, [type='submit']") ||
      null;
    if (btnWrap && btnWrap.parentNode) {
      btnWrap.parentNode.insertBefore(el, btnWrap.nextSibling);
    } else {
      form.appendChild(el);
    }
    return el;
  }

  function setStatus(form, text, kind) {
    var el = ensureStatusEl(form);
    el.textContent = text || "";
    el.setAttribute("data-status-kind", kind || "");
  }

  function findSubmitButton(form) {
    return (
      form.querySelector('button[type="submit"]') ||
      form.querySelector(".msf-submit button") ||
      form.querySelector(".msf-submit") ||
      form.querySelector('input[type="submit"]')
    );
  }

  function getButtonLabel(btn) {
    if (!btn) return "";
    var active = btn.querySelector(".ms-active-string");
    if (active) return active.textContent;
    if (btn.tagName === "INPUT") return btn.value || "";
    return btn.textContent || "";
  }

  function setButtonLabel(btn, text) {
    if (!btn) return;
    var active = btn.querySelector(".ms-active-string");
    if (active) {
      active.textContent = text;
      return;
    }
    if (btn.tagName === "INPUT") {
      btn.value = text;
      return;
    }
    btn.textContent = text;
  }

  function validate(fields, form) {
    if (typeof form.checkValidity === "function" && !form.checkValidity()) {
      if (typeof form.reportValidity === "function") form.reportValidity();
      return "Проверьте поля формы.";
    }
    var phone = trim(fields.phone || "");
    if (phone.length < 5) {
      return "Укажите телефон.";
    }
    var email = trim(fields.email || "");
    if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      return "Проверьте e-mail.";
    }
    return "";
  }

  function trackSuccess(formName, leadId) {
    try {
      window.dataLayer = window.dataLayer || [];
      window.dataLayer.push({
        event: "generate_lead",
        form_name: formName,
        lead_id: leadId,
        page_url: window.location.href,
      });
    } catch (e) {}
    try {
      if (
        typeof window.YANDEX_METRIKA_ID !== "undefined" &&
        window.YANDEX_METRIKA_ID &&
        typeof window.ym === "function"
      ) {
        window.ym(window.YANDEX_METRIKA_ID, "reachGoal", "lead_form_sent", {
          form_name: formName,
          lead_id: leadId,
        });
      }
    } catch (e) {}
  }

  function clearUserFields(form) {
    var controls = form.querySelectorAll("input, textarea, select");
    for (var i = 0; i < controls.length; i++) {
      var el = controls[i];
      var typ = (el.getAttribute("type") || "").toLowerCase();
      if (
        typ === "hidden" ||
        typ === "submit" ||
        typ === "button" ||
        el.name === "ms_meta" ||
        el.name === "website"
      ) {
        continue;
      }
      if (typ === "checkbox" || typ === "radio") {
        // keep regulation consent unchecked? leave as-is for UX of required consent next time
        continue;
      }
      el.value = "";
    }
  }

  function maybeClosePopup(form) {
    // Keep popup open so the in-form success message stays visible.
    // Mottor UI does not auto-close on submit; do not invent close behavior.
    void form;
  }

  async function submitLead(form) {
    if (form.getAttribute("data-lead-submitting") === "1") return;

    var fields = collectFields(form);
    // honeypot
    if (trim(fields.website || "")) {
      setStatus(
        form,
        "Спасибо! Заявка отправлена. Мы скоро свяжемся с вами.",
        "success"
      );
      clearUserFields(form);
      return;
    }

    var err = validate(fields, form);
    if (err) {
      setStatus(form, err, "error");
      return;
    }

    var formName =
      form.getAttribute("data-form-name") ||
      form.dataset.formName ||
      "Форма заявки";
    var utms = resolveUtms();
    var payload = {
      name: fields.name || "",
      phone: fields.phone || "",
      email: fields.email || "",
      message: buildMessage(fields),
      form_name: formName,
      page_url: window.location.href,
      page_title: document.title || "",
      utm_source: utms.utm_source,
      utm_medium: utms.utm_medium,
      utm_campaign: utms.utm_campaign,
      utm_content: utms.utm_content,
      utm_term: utms.utm_term,
      website: "",
    };

    var btn = findSubmitButton(form);
    var originalLabel = getButtonLabel(btn);
    form.setAttribute("data-lead-submitting", "1");
    if (btn) {
      btn.disabled = true;
      btn.setAttribute("aria-busy", "true");
      setButtonLabel(btn, "Отправляем…");
    }
    setStatus(form, "", "");

    try {
      var res = await fetch(ENDPOINT, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      var data = null;
      try {
        data = await res.json();
      } catch (e) {
        data = null;
      }
      if (!res.ok || !data || data.success !== true) {
        throw new Error(
          (data && (data.error || data.message)) ||
            "HTTP " + res.status
        );
      }
      setStatus(
        form,
        "Спасибо! Заявка отправлена. Мы скоро свяжемся с вами.",
        "success"
      );
      clearUserFields(form);
      trackSuccess(formName, data.lead_id);
      maybeClosePopup(form);
    } catch (e) {
      console.error("[lead-forms] submit failed", e && e.message ? e.message : e);
      setStatus(
        form,
        "Не удалось отправить заявку. Позвоните нам или напишите в WhatsApp.",
        "error"
      );
    } finally {
      form.removeAttribute("data-lead-submitting");
      if (btn) {
        btn.disabled = false;
        btn.removeAttribute("aria-busy");
        setButtonLabel(btn, originalLabel || "Отправить");
      }
    }
  }

  function onSubmit(ev) {
    var form = ev.target;
    if (!form || form.tagName !== "FORM") return;
    if (!form.hasAttribute("data-lead-form")) return;
    ev.preventDefault();
    ev.stopPropagation();
    if (typeof ev.stopImmediatePropagation === "function") {
      ev.stopImmediatePropagation();
    }
    submitLead(form);
  }

  function bindForm(form) {
    if (!form || form.getAttribute("data-lead-initialized") === "1") return;
    form.setAttribute("data-lead-initialized", "1");
    // Disable Mottor remote action to avoid accidental native POST
    if (form.getAttribute("action") && form.getAttribute("action").indexOf("leads/receive") !== -1) {
      form.setAttribute("data-original-action", form.getAttribute("action"));
      form.setAttribute("action", "#");
    }
    // Prefer native constraint validation
    form.removeAttribute("novalidate");
    // ensure status node exists early
    ensureStatusEl(form);
  }

  function scan() {
    var forms = document.querySelectorAll("form[data-lead-form]");
    for (var i = 0; i < forms.length; i++) bindForm(forms[i]);
  }

  // Capture-phase to beat Mottor handlers
  document.addEventListener("submit", onSubmit, true);

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", scan);
  } else {
    scan();
  }

  // Re-scan for dynamically injected popups (idle + debounced to cut main-thread work)
  function attachPopupRescan() {
    try {
      var t = 0;
      var mo = new MutationObserver(function () {
        if (t) clearTimeout(t);
        t = setTimeout(scan, 120);
      });
      mo.observe(document.documentElement, { childList: true, subtree: true });
    } catch (e) {}
  }
  if (typeof window.requestIdleCallback === "function") {
    window.requestIdleCallback(attachPopupRescan, { timeout: 2500 });
  } else {
    setTimeout(attachPopupRescan, 1);
  }

  window.RaskrutovLeadForms = {
    scan: scan,
    endpoint: ENDPOINT,
  };
})();
