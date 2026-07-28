(function () {
  const lot = document.getElementById("lot");
  const chipsNav = document.getElementById("chips");
  const empty = document.getElementById("empty");
  let patches = [];
  let active = "alle";

  function esc(s) {
    const d = document.createElement("div");
    d.textContent = String(s);
    return d.innerHTML;
  }

  function tagRows(kind, items) {
    const label = kind === "feature" ? "[FEATURE]" : "[FIX]";
    return items.map(function (text) {
      return '<li><span class="tag tag--' + kind + '">' + label + "</span> " + esc(text) + "</li>";
    }).join("");
  }

  function renderChips() {
    const projects = ["alle"];
    patches.forEach(function (p) {
      if (projects.indexOf(p.project) === -1) projects.push(p.project);
    });
    chipsNav.innerHTML = projects.map(function (p) {
      return '<button class="chip' + (p === active ? " chip--active" : "") +
        '" data-project="' + esc(p) + '">' + esc(p) + "</button>";
    }).join("");
  }

  function render() {
    lot.querySelectorAll(".entry").forEach(function (n) { n.remove(); });
    const shown = patches.filter(function (p) {
      return active === "alle" || p.project === active;
    });
    empty.hidden = shown.length > 0;
    shown.forEach(function (p, i) {
      const entry = document.createElement("article");
      entry.className = "entry" + (i === 0 ? " entry--latest" : "");
      let html =
        '<div class="entry__echo" aria-hidden="true"></div>' +
        '<header class="entry__head">' +
        '<span class="entry__version">v' + esc(p.version) + "</span>" +
        '<span class="entry__project">' + esc(p.name) + "</span>" +
        '<span class="entry__date">' + esc(p.date) + "</span>" +
        "</header>" +
        '<div class="entry__card">';
      const features = p.features || [];
      const fixes = p.fixes || [];
      const notes = p.member_notes || [];
      if (features.length || fixes.length) {
        html += '<ul class="entry__list">' + tagRows("feature", features) +
          tagRows("fix", fixes) + "</ul>";
      }
      if (notes.length) {
        html += '<div class="entry__member"><p class="entry__member-title">▲ Für Member</p><ul>' +
          notes.map(function (n) { return "<li>" + esc(n) + "</li>"; }).join("") +
          "</ul></div>";
      }
      html += "</div>";
      entry.innerHTML = html;
      lot.appendChild(entry);
    });
  }

  chipsNav.addEventListener("click", function (e) {
    const chip = e.target.closest(".chip");
    if (!chip) return;
    active = chip.dataset.project;
    renderChips();
    render();
  });

  fetch("patches.json")
    .then(function (r) {
      if (!r.ok) throw new Error(r.status);
      return r.json();
    })
    .then(function (data) {
      patches = data.patches || [];
      renderChips();
      render();
    })
    .catch(function () {
      empty.hidden = false;
      empty.textContent = "Changelog konnte nicht geladen werden.";
    });
})();
