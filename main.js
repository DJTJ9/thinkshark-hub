const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

// Footer year
const yearEl = document.getElementById("year");
if (yearEl) yearEl.textContent = new Date().getFullYear();

// Sprache: data-de / data-en + localStorage
const langNodes = document.querySelectorAll("[data-de][data-en]");
const langBtns = document.querySelectorAll(".lang__btn");
const langHrefs = document.querySelectorAll("[data-href-de][data-href-en]");
const langAlts = document.querySelectorAll("[data-alt-de][data-alt-en]");

function applyLang(lang) {
  document.documentElement.lang = lang;
  langNodes.forEach((el) => { el.textContent = el.dataset[lang]; });
  langHrefs.forEach((el) => { el.setAttribute("href", lang === "en" ? el.dataset.hrefEn : el.dataset.hrefDe); });
  langAlts.forEach((el) => { el.alt = lang === "en" ? el.dataset.altEn : el.dataset.altDe; });
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

// Scrolltiefe -> --depth (0..1): treibt den Hintergrundverlauf und sea.js
if (document.body.classList.contains("portfolio")) {
  const root = document.documentElement;
  let depthQueued = false;
  const setDepth = () => {
    const max = root.scrollHeight - window.innerHeight;
    const depth = max > 0 ? Math.min(1, Math.max(0, window.scrollY / max)) : 0;
    root.style.setProperty("--depth", depth.toFixed(3));
    depthQueued = false;
  };
  window.addEventListener("scroll", () => {
    if (!depthQueued) { depthQueued = true; requestAnimationFrame(setDepth); }
  }, { passive: true });
  window.addEventListener("resize", setDepth);
  setDepth();
}

// Tauchgang: Anker-Links fahren mit eigener Kurve in die Tiefe statt zu springen
if (document.body.classList.contains("portfolio")) {
  let dive = 0;
  const cancelDive = () => { cancelAnimationFrame(dive); dive = 0; };
  ["wheel", "touchstart", "keydown"].forEach((ev) => window.addEventListener(ev, cancelDive, { passive: true }));
  // Langsam unter die Oberfläche kippen, Fahrt aufnehmen, weich aufsetzen
  const ease = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);

  document.querySelectorAll('a[href^="#"]').forEach((a) => {
    a.addEventListener("click", (e) => {
      const target = document.getElementById(a.getAttribute("href").slice(1));
      if (!target) return;
      if (reduce) return;
      e.preventDefault();
      cancelDive();
      const from = window.scrollY;
      const margin = parseFloat(getComputedStyle(target).scrollMarginTop) || 0;
      const max = document.documentElement.scrollHeight - window.innerHeight;
      const dist = Math.min(max, Math.max(0, target.getBoundingClientRect().top + from - margin)) - from;
      history.pushState(null, "", "#" + target.id);
      if (!target.hasAttribute("tabindex")) target.setAttribute("tabindex", "-1");
      const land = () => { dive = 0; target.focus({ preventScroll: true }); };
      if (Math.abs(dist) < 2) { land(); return; }
      const duration = Math.min(1700, 800 + Math.abs(dist) * 0.3);
      window.dispatchEvent(new CustomEvent("sea:dive", { detail: { down: dist > 0 } }));
      const t0 = performance.now();
      const step = (now) => {
        const t = Math.min(1, (now - t0) / duration);
        window.scrollTo(0, from + dist * ease(t));
        if (t < 1) dive = requestAnimationFrame(step);
        else land();
      };
      dive = requestAnimationFrame(step);
    });
  });
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

// Fund-Ping: genau ein Sonar-Ping pro Projektbild, beim ersten Reinscrollen
const shots = document.querySelectorAll(".project__shot");
if (shots.length && !reduce) {
  const foundObserver = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (!e.isIntersecting) return;
      e.target.classList.add("is-found");
      foundObserver.unobserve(e.target);
    });
  }, { threshold: 0.5 });
  shots.forEach((s) => foundObserver.observe(s));
}

// Izzy-Clips: nur im Viewport abspielen; reduced motion -> Controls statt Autoplay
const clips = document.querySelectorAll(".clip video");
if (clips.length) {
  if (reduce) {
    clips.forEach((v) => { v.controls = true; });
  } else {
    const clipObserver = new IntersectionObserver((entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) e.target.play().catch(() => {});
        else e.target.pause();
      });
    }, { threshold: 0.4 });
    clips.forEach((v) => clipObserver.observe(v));
  }
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
