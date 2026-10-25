// Light/dark switching. The initial class is set inline in head.html so the
// page doesn't flash; this file follows system changes and wires the toggle.
(function () {
  var root = document.documentElement;

  function stored() {
    try { return localStorage.getItem("appearance"); } catch (e) { return null; }
  }

  function store(value) {
    try { localStorage.setItem("appearance", value); } catch (e) {}
  }

  if (root.getAttribute("data-auto-appearance") === "true" && window.matchMedia) {
    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", function (event) {
      if (stored() === null) root.classList.toggle("dark", event.matches);
    });
  }

  function toggle() {
    var dark = root.classList.toggle("dark");
    store(dark ? "dark" : "light");
  }

  ["appearance-switcher", "appearance-switcher-mobile"].forEach(function (id) {
    var button = document.getElementById(id);
    if (button) button.addEventListener("click", toggle);
  });
})();
