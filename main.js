const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

// Footer year
const yearEl = document.getElementById("year");
if (yearEl) yearEl.textContent = new Date().getFullYear();

// Sprache: data-de / data-en + localStorage
const langNodes = document.querySelectorAll("[data-de][data-en]");
const langBtns = document.querySelectorAll(".lang__btn");
const langHrefs = document.querySelectorAll("[data-href-de][data-href-en]");

function applyLang(lang) {
  document.documentElement.lang = lang;
  langNodes.forEach((el) => { el.textContent = el.dataset[lang]; });
  langHrefs.forEach((el) => { el.setAttribute("href", lang === "en" ? el.dataset.hrefEn : el.dataset.hrefDe); });
  langBtns.forEach((b) => b.classList.toggle("is-active", b.dataset.lang === lang));
  try { localStorage.setItem("lang", lang); } catch (e) { /* Private Mode */ }
}

if (langBtns.length) {
  let saved = "de";
  try { saved = localStorage.getItem("lang") || "de"; } catch (e) { /* Private Mode */ }
  applyLang(saved === "en" ? "en" : "de");
  langBtns.forEach((b) => b.addEventListener("click", () => applyLang(b.dataset.lang)));
}

// Mail-Obfuskation
const mail = document.getElementById("mail");
if (mail) {
  const address = mail.dataset.user + "@" + mail.dataset.domain;
  mail.href = "mailto:" + address;
  mail.textContent = address;
}

// Rail-Marker: Tiefe der sichtbaren Sektion -> Marker-Position
const marker = document.querySelector(".rail__marker");
const sections = document.querySelectorAll("section[data-depth]");
if (marker && sections.length) {
  const MAX_DEPTH = 200;
  const navLinks = document.querySelectorAll('.rail__scale a[href^="#"], .chapters a[href^="#"]');
  const observer = new IntersectionObserver(
    (entries) => {
      const visible = entries.filter((e) => e.isIntersecting);
      if (!visible.length) return;
      const top = visible.sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)[0];
      const depth = Number(top.target.dataset.depth);
      marker.style.setProperty("--pos", (depth / MAX_DEPTH) * 84 + 10);
      const id = top.target.id;
      navLinks.forEach((a) => {
        if (a.getAttribute("href") === "#" + id) a.setAttribute("aria-current", "true");
        else a.removeAttribute("aria-current");
      });
      const activeChapter = document.querySelector('.chapters a[aria-current="true"]');
      if (activeChapter) {
        activeChapter.scrollIntoView({
          block: "nearest",
          inline: "center",
          behavior: reduce ? "auto" : "smooth",
        });
      }
    },
    { rootMargin: "-40% 0px -50% 0px" }
  );
  sections.forEach((s) => observer.observe(s));
}

// Sonar-Ping auf Karten-Hover — nur auf hub.html vorhanden
if (!reduce) {
  document.querySelectorAll(".hub-card").forEach((card) => {
    const ring = card.querySelector(".hub-card__ring");
    if (!ring) return;
    card.addEventListener("pointerenter", (e) => {
      const rect = card.getBoundingClientRect();
      ring.style.left = (e.clientX - rect.left) + "px";
      ring.style.top = (e.clientY - rect.top) + "px";
      ring.classList.remove("ping");
      void ring.offsetWidth;
      ring.classList.add("ping");
    });
  });
}
