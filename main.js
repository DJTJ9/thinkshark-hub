// Footer year
document.getElementById("year").textContent = new Date().getFullYear();

// Sonar-Ping on hover — respects reduced motion
const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

if (!reduce) {
  document.querySelectorAll(".hub-card").forEach((card) => {
    const ring = card.querySelector(".hub-card__ring");
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
