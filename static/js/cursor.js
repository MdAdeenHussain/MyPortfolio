(() => {
  const dot = document.querySelector('.cursor-dot');
  const ring = document.querySelector('.cursor-ring');
  if (!dot || !ring) return;

  const supportsHover = window.matchMedia('(hover: hover)').matches;
  if (!supportsHover) return;

  let mouseX = 0;
  let mouseY = 0;
  let ringX = 0;
  let ringY = 0;
  const lerpFactor = 0.12;

  function onMove(e) {
    mouseX = e.clientX;
    mouseY = e.clientY;
    dot.style.transform = `translate(${mouseX}px, ${mouseY}px)`;
  }

  function animate() {
    ringX += (mouseX - ringX) * lerpFactor;
    ringY += (mouseY - ringY) * lerpFactor;
    ring.style.transform = `translate(${ringX}px, ${ringY}px)`;
    requestAnimationFrame(animate);
  }

  document.addEventListener('mousemove', onMove, { passive: true });
  requestAnimationFrame(animate);

  function setHover(state) {
    ring.classList.toggle('is-hover', state);
    dot.classList.toggle('is-hover', state);
  }

  document.addEventListener(
    'pointerover',
    (e) => {
      const target = e.target;
      if (!(target instanceof Element)) return;
      if (target.closest('a, button, input, textarea')) setHover(true);
    },
    { passive: true }
  );

  document.addEventListener(
    'pointerout',
    (e) => {
      const target = e.target;
      if (!(target instanceof Element)) return;
      if (target.closest('a, button, input, textarea')) setHover(false);
    },
    { passive: true }
  );
})();

