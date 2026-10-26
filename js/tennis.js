// Lowkey tennis rally under the header: two stick figures trade a ball across a net.
// Faint ink lines in the heading colour; a still frame when the user prefers reduced motion.
(function () {
  'use strict';
  var c = document.getElementById('tennis');
  if (!c) return;
  var ctx = c.getContext('2d'), W, H;
  var ink = getComputedStyle(document.documentElement).getPropertyValue('--heading-color').trim() || '#1b3a5c';
  var still = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var FLIGHT = 2.4;                  // seconds for the ball to cross
  var start = null, lastHit = -1;    // lastHit: time of the most recent stroke

  function resize() {
    var dpr = window.devicePixelRatio || 1;
    W = c.clientWidth; H = c.clientHeight;
    c.width = W * dpr; c.height = H * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  }

  function line(x1, y1, x2, y2) { ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke(); }
  function dot(x, y, r, fill) { ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); fill ? ctx.fill() : ctx.stroke(); }

  // A stick figure standing at (x, ground), facing +1 (right) or -1 (left).
  // swing in [0,1] animates the racket from ready position through the stroke.
  function player(x, ground, facing, swing, bob) {
    var y = ground - bob;
    ctx.lineWidth = 1.4;
    dot(x, y - 25, 3.2, false);                       // head
    line(x, y - 21.5, x, y - 9);                      // torso
    line(x, y - 9, x - 4, y); line(x, y - 9, x + 4, y); // legs
    line(x, y - 18, x - facing * 5, y - 11);          // back arm
    var a = -0.9 + swing * 2.4;                       // racket angle, ready -> follow-through
    var hx = x + facing * 6, hy = y - 15;
    var rx = hx + facing * Math.cos(a) * 9, ry = hy - Math.sin(a) * 9;
    line(x, y - 18, hx, hy);                          // racket arm
    line(hx, hy, rx, ry);                             // handle
    ctx.beginPath(); ctx.ellipse(rx + facing * Math.cos(a) * 3.5, ry - Math.sin(a) * 3.5, 4.2, 3, -a * facing, 0, Math.PI * 2); ctx.stroke();
  }

  function draw(t) {
    ctx.clearRect(0, 0, W, H);
    var ground = H - 9, left = 28, right = W - 28, mid = W / 2;
    ctx.strokeStyle = ink; ctx.fillStyle = ink;

    // court: baseline and net
    ctx.globalAlpha = 0.22; ctx.lineWidth = 1;
    line(8, ground + 0.5, W - 8, ground + 0.5);
    line(mid, ground, mid, ground - 12);
    line(mid - 5, ground - 12, mid + 5, ground - 12);

    // rally: ball flies left->right on even legs, right->left on odd
    var leg = Math.floor(t / FLIGHT), u = (t / FLIGHT) - leg, toRight = leg % 2 === 0;
    var from = toRight ? left + 14 : right - 14, to = toRight ? right - 14 : left + 14;
    var bx = from + (to - from) * u, by = ground - 14 - 26 * Math.sin(Math.PI * u);

    // the hitter follows through just after contact; the receiver loads up as the ball arrives
    var sinceHit = u * FLIGHT, follow = Math.max(0, 1 - sinceHit / 0.5);
    var hitterSwing = 0.35 + 0.65 * Math.sin(Math.min(1, sinceHit / 0.5) * Math.PI) * follow + (1 - follow) * 0.35;
    var receiverSwing = u > 0.75 ? 0.35 - (u - 0.75) / 0.25 * 0.3 : 0.35;
    var bob = Math.sin(t * 2.2) * 0.6;

    ctx.globalAlpha = 0.5;
    player(left, ground, 1, toRight ? hitterSwing : receiverSwing, bob);
    player(right, ground, -1, toRight ? receiverSwing : hitterSwing, -bob);
    ctx.globalAlpha = 0.65; dot(bx, by, 2.2, true);
    ctx.globalAlpha = 1;
  }

  function frame(now) {
    if (start === null) start = now;
    draw((now - start) / 1000 + 1.1);   // start mid-flight so the first frame is already a rally
    if (!still) requestAnimationFrame(frame);
  }

  resize();
  window.addEventListener('resize', function () { resize(); if (still) draw(1.1); });
  if (still) draw(1.1); else requestAnimationFrame(frame);
})();
