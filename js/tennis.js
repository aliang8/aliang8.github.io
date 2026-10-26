// Lowkey tennis rally under the header: a stick figure (left) and a humanoid robot (right)
// trade a ball. Shots vary in depth, speed and arc; players shuffle to reach the ball and
// occasionally miss. Faint ink lines in the heading colour; one still frame under reduced motion.
// Append ?t=SECONDS to the page URL to fast-forward the rally (for screenshots).
(function () {
  'use strict';
  var c = document.getElementById('tennis');
  if (!c) return;
  var ctx = c.getContext('2d'), W = 0, H = 0;
  var ink = getComputedStyle(document.documentElement).getPropertyValue('--heading-color').trim() || '#1b3a5c';
  var still = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var rnd = function (a, b) { return a + Math.random() * (b - a); };

  // --- world state -------------------------------------------------------------------
  var ground, players, shot, pending = false, pauseUntil = 0, nextHitter = 0;
  var STROLL = 16, HURRY = 90;      // px/s: drifting back to the baseline, max pace to reach a ball

  function resize() {
    var dpr = window.devicePixelRatio || 1;
    W = c.clientWidth; H = c.clientHeight;
    c.width = W * dpr; c.height = H * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    ground = H - 9;
    // each player roams their own half; home is near the baseline
    players = [
      { x: 30, home: 30, lo: 22, hi: W * 0.40, facing: 1, kind: 'human', swing: 0.35 },
      { x: W - 30, home: W - 30, lo: W * 0.60, hi: W - 22, facing: -1, kind: 'robot', swing: 0.35 }
    ];
    serve(0, 0);
  }

  // Player `h` hits the ball at time t0 toward a random spot in the opponent's half.
  function serve(h, t0) {
    var hitter = players[h], rcv = players[1 - h];
    var landX = rnd(rcv.lo + 10, rcv.hi - 10);
    shot = {
      hitter: h, t0: t0,
      dur: rnd(1.9, 2.8),
      x0: hitter.x + hitter.facing * 12, x1: landX,
      apex: rnd(14, 34),
      miss: Math.random() < 0.12
    };
    hitter.hitAt = t0;
    rcv.target = landX - rcv.facing * 12;       // stand so the racket meets the ball
    hitter.target = hitter.home + rnd(-12, 12); // drift back toward the baseline
  }

  function step(t, dt) {
    if (pending && t >= pauseUntil) { pending = false; serve(nextHitter, t); }
    if (!pending) {
      var u = (t - shot.t0) / shot.dur;
      if (u >= 1 && !shot.miss) serve(1 - shot.hitter, t);
      else if (u >= 1.45 && shot.miss) {          // ball rolled away; misser walks back, then serves
        pending = true; nextHitter = 1 - shot.hitter; pauseUntil = t + 1.6;
        players[nextHitter].target = players[nextHitter].home;
      }
    }
    var rcv = pending ? null : players[1 - shot.hitter];
    players.forEach(function (p) {
      var d = (p.target || p.home) - p.x, dist = Math.abs(d), v;
      if (p === rcv) {                             // pace so you arrive as the ball does
        var remain = Math.max(0.25, shot.t0 + shot.dur - t);
        v = Math.min(HURRY, dist / remain);
      } else v = STROLL;
      var move = Math.min(dist, v * dt);
      p.x += Math.sign(d) * move;
      p.moving = move > 0.02 && dist > 0.5 && v > 8;
    });
  }

  // --- drawing -----------------------------------------------------------------------
  function line(x1, y1, x2, y2) { ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke(); }
  function dot(x, y, r, fill) { ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); fill ? ctx.fill() : ctx.stroke(); }

  function racket(x, y, facing, swing) {
    var a = -0.9 + swing * 2.4, hx = x + facing * 6, hy = y - 15;
    var rx = hx + facing * Math.cos(a) * 9, ry = hy - Math.sin(a) * 9;
    line(x, y - 18, hx, hy); line(hx, hy, rx, ry);
    ctx.beginPath(); ctx.ellipse(rx + facing * Math.cos(a) * 3.5, ry - Math.sin(a) * 3.5, 4.2, 3, -a * facing, 0, Math.PI * 2); ctx.stroke();
  }

  function human(p, t) {
    var x = p.x, y = ground - Math.sin(t * 2.2) * 0.6, s = p.moving ? Math.sin(t * 14) * 3.5 : 0;
    ctx.lineWidth = 1.4;
    dot(x, y - 25, 3.2, false);
    line(x, y - 21.5, x, y - 9);
    line(x, y - 9, x - 4 + s, y); line(x, y - 9, x + 4 - s, y);
    line(x, y - 18, x - p.facing * 5, y - 11);
    racket(x, y, p.facing, p.swing);
  }

  function robot(p, t) {
    var x = p.x, y = ground, f = p.facing, s = p.moving ? Math.sin(t * 14) * 3.5 : 0;
    ctx.lineWidth = 1.4;
    ctx.strokeRect(x - 3.5, y - 28.5, 7, 6);                // head
    line(x, y - 28.5, x, y - 32); dot(x, y - 32.5, 0.9, true); // antenna
    dot(x + f * 1.6, y - 25.5, 0.8, true);                   // eye
    ctx.strokeRect(x - 3, y - 21.5, 6, 11.5);                // torso
    line(x - 3, y - 10, x - 4 + s, y - 5); line(x - 4 + s, y - 5, x - 5 + s, y); // legs with knees
    line(x + 3, y - 10, x + 4 - s, y - 5); line(x + 4 - s, y - 5, x + 5 - s, y);
    dot(x - 4 + s, y - 5, 1, true); dot(x + 4 - s, y - 5, 1, true);
    line(x - f * 3, y - 19, x - f * 6, y - 15); line(x - f * 6, y - 15, x - f * 5, y - 10); // back arm
    dot(x - f * 6, y - 15, 1, true);
    racket(x, y, f, p.swing);
    dot(x + f * 6, y - 15, 1, true);                          // elbow on racket arm
  }

  function draw(t) {
    ctx.clearRect(0, 0, W, H);
    ctx.strokeStyle = ink; ctx.fillStyle = ink;
    var mid = W / 2;

    ctx.globalAlpha = 0.22; ctx.lineWidth = 1;
    line(8, ground + 0.5, W - 8, ground + 0.5);
    line(mid, ground, mid, ground - 12); line(mid - 5, ground - 12, mid + 5, ground - 12);

    var u = (t - shot.t0) / shot.dur, hitter = players[shot.hitter], rcv = players[1 - shot.hitter];
    var since = t - hitter.hitAt;
    hitter.swing = 0.35 + 0.65 * Math.sin(Math.min(1, since / 0.5) * Math.PI);
    rcv.swing = u > 0.75 && !shot.miss ? 0.35 - Math.min(1, (u - 0.75) / 0.25) * 0.3 : 0.35;

    ctx.globalAlpha = 0.5;
    players.forEach(function (p) { p.kind === 'robot' ? robot(p, t) : human(p, t); });

    if (!pending) {
      var bx = shot.x0 + (shot.x1 - shot.x0) * u, by = ground - 14 - shot.apex * Math.sin(Math.PI * u);
      if (u > 1) { by = Math.min(ground - 2, by); bx += (shot.x1 - shot.x0) * 0.08 * (u - 1); } // missed ball rolls on
      ctx.globalAlpha = u > 1 ? Math.max(0, 0.65 - (u - 1) * 1.4) : 0.65;
      dot(bx, Math.min(by, ground - 2), 2.2, true);
    }
    ctx.globalAlpha = 1;
  }

  // --- loop --------------------------------------------------------------------------
  var start = null, last = 0, warm = +(new URLSearchParams(location.search).get('t')) || 0;
  function frame(now) {
    if (start === null) { start = now; last = 0; }
    var t = (now - start) / 1000;
    while (warm > 0) { step(last, 1 / 60); last += 1 / 60; warm -= 1 / 60; t += 1 / 60; }
    step(t, Math.min(0.1, t - last)); last = t;
    draw(t);
    if (!still) requestAnimationFrame(frame);
  }

  resize();
  window.addEventListener('resize', function () { resize(); if (still) frame(performance.now()); });
  requestAnimationFrame(frame);
})();
