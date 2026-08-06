(function () {
  "use strict";

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
