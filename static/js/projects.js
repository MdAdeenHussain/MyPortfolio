(() => {
  const disabledLinks = document.querySelectorAll('a[data-disabled="true"]');
  disabledLinks.forEach((a) => {
    a.addEventListener('click', (e) => e.preventDefault());
  });

  const strip = document.querySelector('[data-drag-scroll="true"]');
  if (!strip) return;

  let isDown = false;
  let startX = 0;
  let scrollLeft = 0;

  strip.addEventListener('pointerdown', (e) => {
    isDown = true;
    startX = e.clientX;
    scrollLeft = strip.scrollLeft;
    strip.setPointerCapture(e.pointerId);
  });

  strip.addEventListener('pointerup', () => {
    isDown = false;
  });

  strip.addEventListener('pointercancel', () => {
    isDown = false;
  });

  strip.addEventListener('pointermove', (e) => {
    if (!isDown) return;
    const dx = e.clientX - startX;
    strip.scrollLeft = scrollLeft - dx;
  });
})();

