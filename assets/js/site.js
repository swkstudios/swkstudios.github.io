// Two jobs only: mark the nav link (or the Contact button) for the section in view, and pause the map off-screen.
(function () {
  "use strict";

  // Active section = the last section whose top has crossed a fixed line 40% down the
  // viewport. Position-based, so it switches at the same point scrolling down or up.
  // A section without its own link (data-nav) keeps the highlight of the one it names.
  var links = document.querySelectorAll(".nav-link, .nav-cta[href^='#']");
  var byId = {};
  links.forEach(function (a) { byId[a.getAttribute("href").slice(1)] = a; });
  var sections = Array.prototype.slice.call(document.querySelectorAll("main > section[id]"));
  var current = null;
  var queued = false;

  function update() {
    queued = false;
    var line = window.innerHeight * 0.4;
    var active = null;
    for (var i = 0; i < sections.length; i++) {
      if (sections[i].getBoundingClientRect().top <= line) active = sections[i];
      else break;
    }
    // At the bottom of the page the last sections may never reach the line (tall viewports).
    // Then the section named in the URL hash wins if it is on screen, else the last section.
    var root = document.documentElement;
    if (window.innerHeight + window.pageYOffset >= root.scrollHeight - 2) {
      var named = location.hash ? document.getElementById(location.hash.slice(1)) : null;
      var top = named && sections.indexOf(named) >= 0 ? named.getBoundingClientRect().top : -1;
      active = top >= 0 && top < window.innerHeight ? named : sections[sections.length - 1];
    }
    var link = active ? byId[active.getAttribute("data-nav") || active.id] || null : null;
    if (link === current) return;
    if (current) current.removeAttribute("aria-current");
    if (link) link.setAttribute("aria-current", "location");
    current = link;
  }
  function queue() {
    if (!queued) { queued = true; window.requestAnimationFrame(update); }
  }
  if (links.length && sections.length) {
    window.addEventListener("scroll", queue, { passive: true });
    window.addEventListener("resize", queue);
    window.addEventListener("load", queue);
    window.addEventListener("hashchange", queue);
    update();
  }

  var topo = document.querySelector(".topo");
  if (topo && "IntersectionObserver" in window) {
    new IntersectionObserver(function (entries) {
      topo.classList.toggle("topo--paused", !entries[0].isIntersecting);
    }).observe(topo);
  }
})();
