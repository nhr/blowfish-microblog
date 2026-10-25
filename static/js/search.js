// Search over /archive/index.json (see layouts/list.archivejson.json).
// The index is fetched the first time someone types. Every word in the
// query must appear in a post's title, text or categories; title matches
// rank first. Results are built with DOM methods, never innerHTML.
(function () {
  var section = document.querySelector("[data-search]");
  if (!section) return;

  var input = section.querySelector("input[type=search]");
  // The box sits in the page header; status and results are in the body
  var status = document.querySelector(".search-status");
  var list = document.querySelector(".search-results");
  var category = section.getAttribute("data-category");
  var hidden = document.querySelectorAll("[data-search-hide]");
  var MAX_RESULTS = 30;
  var index = null;
  var loading = null;

  function load() {
    if (!loading) {
      loading = fetch(section.getAttribute("data-index"))
        .then(function (response) { return response.json(); })
        .then(function (feed) {
          index = (feed.items || []).map(function (item) {
            var tags = item.tags || [];
            return {
              item: item,
              title: (item.title || "").toLowerCase(),
              text: (item.content_text || "").toLowerCase(),
              tags: tags.map(function (t) { return t.toLowerCase(); }),
              keys: tags.map(key)
            };
          });
        });
    }
    return loading;
  }

  function scope() {
    var checked = section.querySelector("input[name=search-scope]:checked");
    return checked ? checked.value : "all";
  }

  // Category names can differ in case or punctuation between a post's
  // front matter and the category page title, so compare a normal form
  function key(name) {
    return name.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
  }

  function words(query) {
    return query.toLowerCase().split(/\s+/).filter(Boolean);
  }

  function search(query) {
    var terms = words(query);
    var onlyCategory = category && scope() === "category" ? key(category) : null;
    var matches = [];
    index.forEach(function (entry) {
      if (onlyCategory && entry.keys.indexOf(onlyCategory) === -1) return;
      var score = 0;
      for (var i = 0; i < terms.length; i++) {
        var t = terms[i];
        var inTitle = entry.title.indexOf(t) !== -1;
        if (!inTitle && entry.text.indexOf(t) === -1 && !entry.tags.some(function (tag) { return tag.indexOf(t) !== -1; })) {
          return;
        }
        score += inTitle ? 10 : 1;
      }
      matches.push({ entry: entry, score: score });
    });
    // Higher score first; the index is already newest first, and sort is stable
    matches.sort(function (a, b) { return b.score - a.score; });
    return matches;
  }

  // Text around the first match, so the snippet shows why a post matched
  function snippet(text, terms) {
    var lower = text.toLowerCase();
    var at = -1;
    for (var i = 0; i < terms.length && at === -1; i++) at = lower.indexOf(terms[i]);
    var start = Math.max(0, at - 60);
    var out = text.substr(start, 200).replace(/\s+/g, " ").trim();
    return (start > 0 ? "…" : "") + out + (start + 200 < text.length ? "…" : "");
  }

  // Append text to el, wrapping each occurrence of the terms in <mark>
  function highlight(el, text, terms) {
    if (!terms.length) { el.appendChild(document.createTextNode(text)); return; }
    var escaped = terms.map(function (t) { return t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); });
    var parts = text.split(new RegExp("(" + escaped.join("|") + ")", "ig"));
    parts.forEach(function (part, i) {
      if (i % 2) {
        var mark = document.createElement("mark");
        mark.textContent = part;
        el.appendChild(mark);
      } else if (part) {
        el.appendChild(document.createTextNode(part));
      }
    });
  }

  function formatDate(iso) {
    var d = new Date(iso);
    return isNaN(d) ? "" : d.toLocaleDateString(undefined, { year: "numeric", month: "long", day: "numeric" });
  }

  function render(query) {
    var terms = words(query);
    list.textContent = "";
    if (!terms.length) {
      status.classList.add("hidden");
      hidden.forEach(function (el) { el.classList.remove("hidden"); });
      return;
    }
    hidden.forEach(function (el) { el.classList.add("hidden"); });
    var matches = search(query);
    status.classList.remove("hidden");
    status.textContent = matches.length === 0 ? "No posts found." :
      matches.length === 1 ? "1 post found." :
      matches.length > MAX_RESULTS ? matches.length + " posts found, showing the first " + MAX_RESULTS + "." :
      matches.length + " posts found.";

    matches.slice(0, MAX_RESULTS).forEach(function (match) {
      var item = match.entry.item;
      var li = document.createElement("li");
      li.className = "mb-2";
      var a = document.createElement("a");
      a.className = "flex items-center px-3 py-2 rounded-md appearance-none bg-neutral-100 dark:bg-neutral-700 focus:bg-primary-100 hover:bg-primary-100 dark:hover:bg-primary-900 dark:focus:bg-primary-900 focus:outline-dotted focus:outline-transparent focus:outline-2";
      a.href = item.url;
      var body = document.createElement("div");
      body.className = "grow";
      var title = document.createElement("div");
      title.className = "text-lg font-bold";
      highlight(title, item.title || snippet(item.content_text || "", terms).slice(0, 80), terms);
      var meta = document.createElement("div");
      meta.className = "text-sm text-neutral-500 dark:text-neutral-400";
      meta.textContent = formatDate(item.date_published) + ((item.tags || []).length ? " · " + item.tags.join(", ") : "");
      body.appendChild(title);
      body.appendChild(meta);
      if (item.title && item.content_text) {
        var summary = document.createElement("div");
        summary.className = "text-sm";
        highlight(summary, snippet(item.content_text, terms), terms);
        body.appendChild(summary);
      }
      var arrow = document.createElement("div");
      arrow.className = "ml-2 text-neutral-500";
      arrow.textContent = "→";
      a.appendChild(body);
      a.appendChild(arrow);
      li.appendChild(a);
      list.appendChild(li);
    });
  }

  // Keep the query in the address bar so a search can be shared or revisited
  function remember(query) {
    var url = new URL(window.location.href);
    if (query) url.searchParams.set("q", query); else url.searchParams.delete("q");
    history.replaceState(null, "", url);
  }

  var timer = null;
  function update() {
    var query = input.value.trim();
    clearTimeout(timer);
    timer = setTimeout(function () {
      load().then(function () { render(query); remember(query); });
    }, 150);
  }

  input.addEventListener("input", update);
  input.addEventListener("focus", load, { once: true });
  section.querySelectorAll("input[name=search-scope]").forEach(function (radio) {
    radio.addEventListener("change", update);
  });

  var initial = new URLSearchParams(window.location.search).get("q");
  if (initial) {
    input.value = initial;
    update();
  }
})();
