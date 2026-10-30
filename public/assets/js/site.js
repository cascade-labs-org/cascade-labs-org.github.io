// Cascade Labs - the only script on the site. Everything works without it; it adds the
// riffle you get by hovering or tapping the fan on the home page.
(function () {
  document.documentElement.classList.add('js');
  var fan = document.querySelector('.fan');
  if (!fan) return;
  var stage = fan.closest('.fan-stage');
  var still = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // The opening fan is pure CSS. Once it has played, mark it done so that switching the
  // animation off and on for a riffle never replays the opening.
  var opened = false;
  function done() {
    if (opened) return;
    opened = true;
    fan.classList.add('done');
  }
  if (still) done();
  else setTimeout(done, 2100);

  var busy = false;
  function riffle() {
    if (!opened || busy || still) return;
    busy = true;
    fan.classList.add('riffle');
    setTimeout(function () {
      fan.classList.remove('riffle');
      busy = false;
    }, 1250);
  }
  stage.addEventListener('pointerenter', function (e) {
    if (e.pointerType === 'mouse') riffle();
  });
  stage.addEventListener('click', riffle);
})();
