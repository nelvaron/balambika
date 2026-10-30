/**
 * Glyph globe: a sphere of letters from three scripts, slowly turning, with
 * arcs that travel between letters that transliterate one another
 * (Devanagari → IAST → Bulgarian Cyrillic).
 *
 * Canvas 2D, no dependencies. Honours prefers-reduced-motion, pauses when
 * off screen or in a background tab, and can be paused by the visitor.
 */

type Script = 'deva' | 'latn' | 'cyrl';
type Vec = [number, number, number];

interface Point {
  v: Vec;
  glyph: string;
  script: Script;
  scale: number;
  glow: number; // 0..1, decays
}

interface Arc {
  from: Point;
  to: Point;
  start: number; // ms
  duration: number;
  hold: number;
}

const TRIPLES: [string, string, string][] = [
  ['क', 'k', 'к'], ['ग', 'g', 'г'], ['ज', 'j', 'дж'], ['त', 't', 'т'],
  ['द', 'd', 'д'], ['न', 'n', 'н'], ['प', 'p', 'п'], ['ब', 'b', 'б'],
  ['म', 'm', 'м'], ['य', 'y', 'й'], ['र', 'r', 'р'], ['ल', 'l', 'л'],
  ['व', 'v', 'в'], ['श', 'ś', 'ш'], ['स', 's', 'с'], ['ह', 'h', 'х'],
  ['अ', 'a', 'а'], ['इ', 'i', 'и'], ['उ', 'u', 'у'], ['ए', 'e', 'е'],
  ['ओ', 'o', 'о'], ['च', 'c', 'ч'], ['ष', 'ṣ', 'ш'], ['ऋ', 'ṛ', 'ри'],
  ['ज्ञ', 'jñ', 'джн'], ['क्ष', 'kṣ', 'кш'], ['श्री', 'śrī', 'шри'], ['ॐ', 'oṃ', 'ом'],
  ['भ', 'bh', 'бх'], ['ध', 'dh', 'дх'], ['ण', 'ṇ', 'н'], ['ट', 'ṭ', 'т'],
];

const FILL: Record<Script, string[]> = {
  deva: [...'आईऊऐऔखघङछझञठडढथफ'].concat(['त्र', 'द्ध', 'द्य', 'ह्म', 'न्द्र', 'स्त्र', 'क्ष्म्य', 'त्त्व', 'ङ्ग', 'ञ्च', 'ण्ड', 'श्व', 'ऽ', '॥', '१', '२', '३', '४', '५']),
  latn: [...'āīūṝḷṅñḍṭṇṣśṃḥAĀBDGHIĪKMNPRṚSŚṢTUŪVY'],
  cyrl: [...'жщъьюяцфзАБВГДЖЗИЙЛПФЦЧШЩЪЮЯ'],
};

const COLORS: Record<Script, [number, number, number]> = {
  deva: [168, 216, 179],
  latn: [228, 194, 122],
  cyrl: [143, 176, 204],
};

const rgba = ([r, g, b]: [number, number, number], a: number) => `rgba(${r},${g},${b},${a.toFixed(3)})`;

// The globe follows the site-wide face switch (data-face on <html>).
const face = () => (document.documentElement.dataset.face === 'sans' ? 'sans' : 'serif');
const family = () => (face() === 'sans' ? "'Balambika Sans', Balambika, sans-serif" : 'Balambika, serif');

function fibonacciSphere(n: number): Vec[] {
  const pts: Vec[] = [];
  const phi = Math.PI * (3 - Math.sqrt(5));
  for (let i = 0; i < n; i++) {
    const y = 1 - (i / (n - 1)) * 2;
    const r = Math.sqrt(1 - y * y);
    const th = phi * i;
    pts.push([Math.cos(th) * r, y, Math.sin(th) * r]);
  }
  return pts;
}

function rotate([x, y, z]: Vec, yaw: number, pitch: number): Vec {
  const cy = Math.cos(yaw), sy = Math.sin(yaw);
  const x1 = x * cy + z * sy;
  const z1 = -x * sy + z * cy;
  const cp = Math.cos(pitch), sp = Math.sin(pitch);
  const y2 = y * cp - z1 * sp;
  const z2 = y * sp + z1 * cp;
  return [x1, y2, z2];
}

function slerp(a: Vec, b: Vec, t: number): Vec {
  const dot = Math.min(1, Math.max(-1, a[0] * b[0] + a[1] * b[1] + a[2] * b[2]));
  const om = Math.acos(dot);
  if (om < 1e-4) return a;
  const s = Math.sin(om);
  const k1 = Math.sin((1 - t) * om) / s, k2 = Math.sin(t * om) / s;
  return [a[0] * k1 + b[0] * k2, a[1] * k1 + b[1] * k2, a[2] * k1 + b[2] * k2];
}

function shuffle<T>(arr: T[], rnd: () => number): T[] {
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(rnd() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

// Deterministic PRNG so the globe looks the same on every load.
function mulberry32(seed: number) {
  return () => {
    seed |= 0; seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export function mountGlobe(root: HTMLElement) {
  const canvas = root.querySelector('canvas')!;
  const ctx = canvas.getContext('2d')!;
  const button = root.querySelector<HTMLButtonElement>('[data-globe-toggle]')!;
  const caption = root.querySelector<HTMLElement>('[data-globe-caption]');
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)');

  const rnd = mulberry32(108);
  const N = 240;
  const slots = shuffle(fibonacciSphere(N), rnd);
  const points: Point[] = [];
  const triples: [Point, Point, Point][] = [];

  let k = 0;
  for (const [d, l, c] of TRIPLES) {
    const tri = ([['deva', d], ['latn', l], ['cyrl', c]] as [Script, string][]).map(([script, glyph]) => {
      const p: Point = { v: slots[k++], glyph, script, scale: 1.15, glow: 0 };
      points.push(p);
      return p;
    }) as [Point, Point, Point];
    triples.push(tri);
  }
  const scripts: Script[] = ['deva', 'latn', 'cyrl'];
  while (k < N) {
    const script = scripts[k % 3];
    const pool = FILL[script];
    points.push({ v: slots[k++], glyph: pool[Math.floor(rnd() * pool.length)], script, scale: 0.75 + rnd() * 0.3, glow: 0 });
  }

  // Graticule: parallels every 30°, meridians every 30°.
  const graticule: Vec[][] = [];
  for (let lat = -60; lat <= 60; lat += 30) {
    const ring: Vec[] = [];
    const y = Math.sin((lat * Math.PI) / 180), r = Math.cos((lat * Math.PI) / 180);
    for (let i = 0; i <= 96; i++) {
      const a = (i / 96) * Math.PI * 2;
      ring.push([Math.cos(a) * r, y, Math.sin(a) * r]);
    }
    graticule.push(ring);
  }
  for (let lon = 0; lon < 180; lon += 30) {
    const ring: Vec[] = [];
    const a = (lon * Math.PI) / 180;
    for (let i = 0; i <= 96; i++) {
      const t = (i / 96) * Math.PI * 2;
      ring.push([Math.cos(t) * Math.cos(a), Math.sin(t), Math.cos(t) * Math.sin(a)]);
    }
    graticule.push(ring);
  }

  let width = 0, height = 0, dpr = 1;
  let yaw = 0.6, pitch = -0.32;
  let velocity = 0;
  const AUTO = 0.00012; // rad per ms
  let playing = !reduce.matches;
  let visible = true;
  let raf = 0;
  let last = performance.now();
  let arcs: Arc[] = [];
  let nextTriple = 0;
  let tripleIndex = 0;

  function resize() {
    const rect = canvas.getBoundingClientRect();
    dpr = Math.min(2, window.devicePixelRatio || 1);
    width = rect.width; height = rect.height;
    canvas.width = Math.round(width * dpr);
    canvas.height = Math.round(height * dpr);
    draw(performance.now());
  }

  function project(v: Vec) {
    const r = rotate(v, yaw, pitch);
    const R = Math.min(width, height) * 0.4;
    return { x: width / 2 + r[0] * R, y: height / 2 - r[1] * R, z: r[2], R };
  }

  function launchTriple(now: number) {
    const [d, l, c] = triples[tripleIndex++ % triples.length];
    arcs.push({ from: d, to: l, start: now, duration: 1300, hold: 900 });
    arcs.push({ from: l, to: c, start: now + 1300, duration: 1300, hold: 900 });
    if (caption) {
      const spans = caption.querySelectorAll('span');
      spans[0].textContent = d.glyph;
      spans[1].textContent = l.glyph;
      spans[2].textContent = c.glyph;
      caption.classList.remove('is-fresh');
      void caption.offsetWidth;
      caption.classList.add('is-fresh');
    }
  }

  function drawArc(arc: Arc, now: number) {
    const elapsed = now - arc.start;
    if (elapsed < 0) return;
    const t = Math.min(1, elapsed / arc.duration);
    const fade = elapsed > arc.duration ? 1 - Math.min(1, (elapsed - arc.duration) / arc.hold) : 1;
    const a = arc.from.v, b = arc.to.v;
    const dot = a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
    const lift = 0.08 + 0.14 * (Math.acos(Math.max(-1, Math.min(1, dot))) / Math.PI);
    const steps = 48;
    const from = COLORS[arc.from.script], to = COLORS[arc.to.script];
    let prev: ReturnType<typeof project> | null = null;
    const n = Math.max(1, Math.round(steps * t));
    for (let i = 0; i <= n; i++) {
      const s = (i / steps);
      const v = slerp(a, b, s);
      const h = 1 + lift * Math.sin(Math.PI * s);
      const p = project([v[0] * h, v[1] * h, v[2] * h]);
      if (prev) {
        const mix: [number, number, number] = [0, 1, 2].map((j) => from[j] + (to[j] - from[j]) * s) as [number, number, number];
        const depth = p.z > -0.15 ? 1 : 0.25;
        const tail = Math.pow(i / n, 1.6);
        ctx.strokeStyle = rgba(mix, (0.15 + 0.85 * tail) * depth * fade);
        ctx.lineWidth = 1.6;
        ctx.beginPath();
        ctx.moveTo(prev.x, prev.y);
        ctx.lineTo(p.x, p.y);
        ctx.stroke();
      }
      prev = p;
    }
    if (prev && t < 1) {
      ctx.fillStyle = rgba(to, 0.95 * fade);
      ctx.beginPath();
      ctx.arc(prev.x, prev.y, 3, 0, Math.PI * 2);
      ctx.fill();
    }
    if (t < 1) arc.from.glow = Math.max(arc.from.glow, 1 - t * 0.5);
    else arc.to.glow = Math.max(arc.to.glow, fade);
  }

  function draw(now: number) {
    if (!width) return;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, width, height);
    const R = Math.min(width, height) * 0.4;
    const cx = width / 2, cy = height / 2;

    // Halo and rim.
    const halo = ctx.createRadialGradient(cx, cy, R * 0.6, cx, cy, R * 1.25);
    halo.addColorStop(0, 'rgba(45,106,59,0.18)');
    halo.addColorStop(1, 'rgba(45,106,59,0)');
    ctx.fillStyle = halo;
    ctx.fillRect(0, 0, width, height);
    ctx.strokeStyle = 'rgba(168,216,179,0.22)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.arc(cx, cy, R, 0, Math.PI * 2);
    ctx.stroke();

    // Graticule, back half then front half.
    for (const front of [false, true]) {
      ctx.beginPath();
      for (const ring of graticule) {
        let prev: ReturnType<typeof project> | null = null;
        for (const v of ring) {
          const p = project(v);
          if (prev && (p.z + prev.z > 0) === front) {
            ctx.moveTo(prev.x, prev.y);
            ctx.lineTo(p.x, p.y);
          }
          prev = p;
        }
      }
      ctx.strokeStyle = front ? 'rgba(176,189,182,0.16)' : 'rgba(176,189,182,0.05)';
      ctx.setLineDash(front ? [2, 4] : [1, 6]);
      ctx.stroke();
    }
    ctx.setLineDash([]);

    // Arcs behind the letters' front layer.
    arcs = arcs.filter((a) => now - a.start < a.duration + a.hold);
    for (const arc of arcs) drawArc(arc, now);

    // Letters, back to front.
    const projected = points.map((pt) => ({ pt, p: project(pt.v) })).sort((a, b) => a.p.z - b.p.z);
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    const base = Math.max(11, R * 0.085);
    for (const { pt, p } of projected) {
      const depth = (p.z + 1) / 2; // 0 back, 1 front
      const glow = pt.glow;
      const size = base * pt.scale * (0.55 + 0.6 * depth) * (1 + glow * 0.6);
      const alpha = Math.min(1, 0.08 + 0.92 * Math.pow(depth, 1.8) + glow * 0.8);
      const weight = glow > 0.2 || pt.scale > 1.1 ? 500 : 400;
      const italic = pt.script === 'latn' ? 'italic ' : '';
      ctx.font = `${italic}${weight} ${size.toFixed(1)}px ${family()}`;
      if (glow > 0.05) {
        ctx.shadowColor = rgba(COLORS[pt.script], 0.9 * glow);
        ctx.shadowBlur = 18 * glow;
      }
      ctx.fillStyle = rgba(COLORS[pt.script], alpha);
      ctx.fillText(pt.glyph, p.x, p.y);
      ctx.shadowBlur = 0;
      pt.glow *= 0.965;
    }
  }

  function frame(now: number) {
    const dt = Math.min(64, now - last);
    last = now;
    if (!dragging) {
      yaw += AUTO * dt + velocity * dt;
      velocity *= Math.pow(0.995, dt);
    }
    if (now > nextTriple) {
      launchTriple(now);
      nextTriple = now + 1900;
    }
    draw(now);
    raf = requestAnimationFrame(frame);
  }

  function start() {
    if (raf || !playing || !visible) return;
    last = performance.now();
    raf = requestAnimationFrame(frame);
  }
  function stop() {
    cancelAnimationFrame(raf);
    raf = 0;
  }
  function setPlaying(value: boolean) {
    playing = value;
    button.setAttribute('aria-pressed', String(!value));
    button.querySelector('[data-label]')!.textContent = value ? button.dataset.pause! : button.dataset.play!;
    if (value) start(); else { stop(); draw(performance.now()); }
  }

  // A still frame for reduced motion: three finished arcs, no movement.
  function staticFrame() {
    const now = performance.now();
    arcs = [];
    for (let i = 0; i < 3; i++) {
      const [d, l, c] = triples[(i * 7) % triples.length];
      arcs.push({ from: d, to: l, start: now - 1300, duration: 1300, hold: 1e9 });
      arcs.push({ from: l, to: c, start: now - 1300, duration: 1300, hold: 1e9 });
    }
    draw(now);
  }

  // Dragging: horizontal turns the globe; vertical scroll stays with the page.
  let dragging = false;
  let lastX = 0, lastT = 0;
  canvas.addEventListener('pointerdown', (e) => {
    dragging = true; lastX = e.clientX; lastT = performance.now();
    canvas.setPointerCapture(e.pointerId);
  });
  canvas.addEventListener('pointermove', (e) => {
    if (!dragging) return;
    const now = performance.now();
    const dx = e.clientX - lastX;
    yaw += dx * 0.006;
    velocity = (dx * 0.006) / Math.max(8, now - lastT) * 0.6;
    lastX = e.clientX; lastT = now;
    if (!raf) draw(now);
  });
  const end = () => { dragging = false; };
  canvas.addEventListener('pointerup', end);
  canvas.addEventListener('pointercancel', end);

  button.addEventListener('click', () => setPlaying(!playing));

  new ResizeObserver(resize).observe(canvas);
  new IntersectionObserver(([entry]) => {
    visible = entry.isIntersecting;
    if (visible) start(); else stop();
  }).observe(root);
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) stop(); else start();
  });
  reduce.addEventListener('change', () => {
    setPlaying(!reduce.matches);
    if (reduce.matches) staticFrame();
  });

  function loadFonts(): Promise<unknown> {
    if (!document.fonts) return Promise.resolve();
    const name = face() === 'sans' ? "'Balambika Sans'" : 'Balambika';
    return Promise.race([
      Promise.all([
        document.fonts.load(`400 32px ${name}`, 'कkк'),
        document.fonts.load(`500 32px ${name}`, 'कkк'),
        document.fonts.load(`italic 400 32px ${name}`, 'ā'),
      ]),
      new Promise((r) => setTimeout(r, 2000)),
    ]);
  }

  const ready = loadFonts();

  // Follow the site-wide face switch: load the other family, then redraw.
  document.documentElement.addEventListener('facechange', () => {
    loadFonts().then(() => {
      if (!playing) staticFrame();
    });
  });

  ready.then(() => {
    root.classList.add('is-ready');
    resize();
    setPlaying(playing);
    if (!playing) staticFrame();
  });
}
