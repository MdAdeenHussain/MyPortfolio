(() => {
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const cards = document.querySelectorAll('.service-card[data-particle]');
  if (!cards.length) return;

  function cssVar(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  }

  const accent = cssVar('--color-accent');
  const accentDim = cssVar('--color-accent-dim');
  const border = cssVar('--color-border');

  function setupCanvas(canvas) {
    const ctx = canvas.getContext('2d');
    const dpr = Math.min(window.devicePixelRatio || 1, 2);

    function resize() {
      const rect = canvas.getBoundingClientRect();
      canvas.width = Math.floor(rect.width * dpr);
      canvas.height = Math.floor(rect.height * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }

    resize();
    window.addEventListener('resize', resize, { passive: true });

    return { ctx, resize };
  }

  function sphere(canvas) {
    const { ctx } = setupCanvas(canvas);
    const dots = [];
    const dotCount = window.matchMedia('(min-width: 768px)').matches ? 600 : 300;

    function init() {
      dots.length = 0;
      for (let i = 0; i < dotCount; i++) {
        const u = Math.random() * 2 - 1;
        const t = Math.random() * Math.PI * 2;
        const r = Math.sqrt(1 - u * u);
        dots.push({ x: r * Math.cos(t), y: u, z: r * Math.sin(t) });
      }
    }

    init();
    let rot = 0;

    function draw() {
      if (reduceMotion) return;
      const w = canvas.clientWidth;
      const h = canvas.clientHeight;
      ctx.clearRect(0, 0, w, h);

      const cx = w * 0.72;
      const cy = h * 0.55;
      const radius = Math.min(w, h) * 0.24;

      rot += 0.004;
      const sin = Math.sin(rot);
      const cos = Math.cos(rot);

      for (const p of dots) {
        const x = p.x * cos - p.z * sin;
        const z = p.x * sin + p.z * cos;
        const y = p.y;

        const depth = (z + 1.6) / 2.6;
        const px = cx + x * radius;
        const py = cy + y * radius;
        const size = 1 + depth * 1.6;
        ctx.globalAlpha = 0.3 + depth * 0.5;
        ctx.fillStyle = accent;
        ctx.beginPath();
        ctx.arc(px, py, size, 0, Math.PI * 2);
        ctx.fill();
      }

      requestAnimationFrame(draw);
    }

    requestAnimationFrame(draw);
  }

  function lock(canvas) {
    const { ctx } = setupCanvas(canvas);
    const points = [];
    const pointCount = window.matchMedia('(min-width: 768px)').matches ? 520 : 260;

    function sampleLock() {
      points.length = 0;
      for (let i = 0; i < pointCount; i++) {
        const x = Math.random();
        const y = Math.random();
        const inBody = y > 0.38 && x > 0.22 && x < 0.78;
        const dx = x - 0.5;
        const inShackle = y < 0.5 && (dx * dx + (y - 0.38) * (y - 0.38)) < 0.15 * 0.15;
        if (inBody || inShackle) points.push({ x, y });
      }
    }

    sampleLock();
    let t = 0;

    function draw() {
      if (reduceMotion) return;
      const w = canvas.clientWidth;
      const h = canvas.clientHeight;
      ctx.clearRect(0, 0, w, h);

      t += 0.02;
      const pulse = 1 + Math.sin(t) * 0.015;

      const ox = w * 0.72;
      const oy = h * 0.54;
      const size = Math.min(w, h) * 0.42;

      ctx.globalAlpha = 0.65;
      ctx.fillStyle = accentDim;

      for (const p of points) {
        const px = ox + (p.x - 0.5) * size * pulse;
        const py = oy + (p.y - 0.5) * size * pulse;
        ctx.beginPath();
        ctx.arc(px, py, 1.5, 0, Math.PI * 2);
        ctx.fill();
      }

      requestAnimationFrame(draw);
    }

    requestAnimationFrame(draw);
  }

  function wave(canvas) {
    const { ctx } = setupCanvas(canvas);
    let phase = 0;

    function draw() {
      if (reduceMotion) return;
      const w = canvas.clientWidth;
      const h = canvas.clientHeight;
      ctx.clearRect(0, 0, w, h);

      const midY = h * 0.58;
      const amp = Math.min(w, h) * 0.08;
      const len = w * 0.7;
      const startX = w * 0.18;

      ctx.lineWidth = 2;
      ctx.strokeStyle = border;
      ctx.beginPath();
      ctx.moveTo(startX, midY);
      ctx.lineTo(startX + len, midY);
      ctx.stroke();

      ctx.strokeStyle = accentDim;
      ctx.beginPath();

      const steps = 120;
      for (let i = 0; i <= steps; i++) {
        const x = startX + (i / steps) * len;
        const y = midY + Math.sin(i * 0.22 + phase) * amp;
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.stroke();

      phase += 0.05;
      requestAnimationFrame(draw);
    }

    requestAnimationFrame(draw);
  }

  function diamond(canvas) {
    const { ctx } = setupCanvas(canvas);
    const dots = [];
    const dotCount = window.matchMedia('(min-width: 768px)').matches ? 400 : 220;

    function init() {
      dots.length = 0;
      for (let i = 0; i < dotCount; i++) {
        const x = Math.random() * 2 - 1;
        const y = Math.random() * 2 - 1;
        const z = Math.random() * 2 - 1;
        const d = Math.abs(x) + Math.abs(y) + Math.abs(z);
        if (d < 1.6) dots.push({ x, y, z });
      }
    }

    init();
    let ax = 0;
    let ay = 0;

    function draw() {
      if (reduceMotion) return;
      const w = canvas.clientWidth;
      const h = canvas.clientHeight;
      ctx.clearRect(0, 0, w, h);

      ax += 0.006;
      ay += 0.004;
      const sinx = Math.sin(ax);
      const cosx = Math.cos(ax);
      const siny = Math.sin(ay);
      const cosy = Math.cos(ay);

      const cx = w * 0.72;
      const cy = h * 0.56;
      const radius = Math.min(w, h) * 0.22;

      for (const p of dots) {
        let y = p.y * cosx - p.z * sinx;
        let z = p.y * sinx + p.z * cosx;
        let x = p.x * cosy - z * siny;
        z = p.x * siny + z * cosy;

        const depth = (z + 2) / 3;
        const px = cx + x * radius;
        const py = cy + y * radius;
        const size = 1 + depth * 1.5;
        ctx.globalAlpha = 0.25 + depth * 0.55;
        ctx.fillStyle = accent;
        ctx.beginPath();
        ctx.arc(px, py, size, 0, Math.PI * 2);
        ctx.fill();
      }

      requestAnimationFrame(draw);
    }

    requestAnimationFrame(draw);
  }

  const renderers = { sphere, lock, wave, diamond };

  cards.forEach((card) => {
    const type = card.getAttribute('data-particle');
    const canvas = card.querySelector('canvas');
    if (!type || !canvas) return;
    const fn = renderers[type];
    if (typeof fn === 'function') fn(canvas);

    const dot = card.querySelector('.service-hover-dot');
    if (dot) {
      card.addEventListener('mousemove', (e) => {
        const rect = card.getBoundingClientRect();
        dot.style.left = `${e.clientX - rect.left}px`;
        dot.style.top = `${e.clientY - rect.top}px`;
      });
    }
  });
})();

