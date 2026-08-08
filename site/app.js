try {
document.addEventListener('DOMContentLoaded', function() {
  var btn = document.querySelector('.nav-toggle');
  var links = document.querySelector('.nav-links');
  console.log('[v13] DOMContentLoaded, btn=', btn, 'links=', links);
  if (btn && links) {
    btn.addEventListener('click', function() {
      var isOpen = links.classList.toggle('open');
      if (isOpen) btn.setAttribute('aria-expanded', 'true');
      else btn.setAttribute('aria-expanded', 'false');
    });
    links.querySelectorAll('a').forEach(function(a) {
      a.addEventListener('click', function() {
        links.classList.remove('open');
        btn.setAttribute('aria-expanded', 'false');
      });
    });
  }
  var cue = document.querySelector('.scroll-cue');
  if (cue) {
    var st = window.pageYOffset || document.documentElement.scrollTop;
    if (st > 100) cue.style.opacity = '0';
  }
  if (typeof IntersectionObserver !== 'undefined') {
    var observer = new IntersectionObserver(function(entries) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting) entry.target.classList.add('visible');
      });
    }, {threshold: 0.1});
    document.querySelectorAll('.fade-up').forEach(function(el) {
      observer.observe(el);
    });
  }
  console.log('[v13] ready');
});
} catch (e) {
  console.error('[v13] init error', e);
}
