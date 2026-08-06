/**
 * Создание сайтов — page-specific interactions.
 * Shared menu/modal/forms live in home-clean.js + lead-forms.js.
 */
(() => {
  const lightbox = document.getElementById("sz-lightbox");
  const lightboxImg = lightbox && lightbox.querySelector("[data-sz-lightbox-img]");
  const triggers = [...document.querySelectorAll("[data-sz-lightbox-src]")];
  if (!lightbox || !lightboxImg || !triggers.length) return;

  let lastFocus = null;

  const close = () => {
    if (lightbox.hidden) return;
    lightbox.hidden = true;
    lightboxImg.removeAttribute("src");
    document.body.style.overflow = "";
    if (lastFocus && typeof lastFocus.focus === "function") lastFocus.focus();
    lastFocus = null;
  };

  const open = (src, alt, trigger) => {
    if (!src) return;
    lastFocus = trigger || document.activeElement;
    lightboxImg.src = src;
    lightboxImg.alt = alt || "";
    lightbox.hidden = false;
    document.body.style.overflow = "hidden";
    const closeBtn = lightbox.querySelector("[data-sz-lightbox-close]");
    if (closeBtn) closeBtn.focus();
  };

  triggers.forEach((btn) => {
    btn.addEventListener("click", () => {
      open(btn.getAttribute("data-sz-lightbox-src"), btn.getAttribute("data-sz-lightbox-alt") || "", btn);
    });
  });

  lightbox.addEventListener("click", (event) => {
    if (event.target === lightbox || event.target.closest("[data-sz-lightbox-close]")) {
      close();
    }
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !lightbox.hidden) close();
  });
})();
