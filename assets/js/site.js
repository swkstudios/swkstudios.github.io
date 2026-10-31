// Two jobs only: mark the nav link for the section in view, and pause the map off-screen.
(function () {
  "use strict";
  if (!("IntersectionObserver" in window)) return;

  var links = document.querySelectorAll(".nav-link");
  var byId = {};
  links.forEach(function (a) { byId[a.getAttribute("href").slice(1)] = a; });

  var navObserver = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (!e.isIntersecting) return;
      links.forEach(function (a) { a.removeAttribute("aria-current"); });
      var link = byId[e.target.id];
      if (link) link.setAttribute("aria-current", "location");
    });
  }, { rootMargin: "-40% 0px -55% 0px" });
  document.querySelectorAll("main > section[id]").forEach(function (s) { navObserver.observe(s); });

  var topo = document.querySelector(".topo");
  if (topo) {
    new IntersectionObserver(function (entries) {
      topo.classList.toggle("topo--paused", !entries[0].isIntersecting);
    }).observe(topo);
  }
})();
