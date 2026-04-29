(() => {
  const splitTargets = document.querySelectorAll('[data-split="true"]');
  if (!splitTargets.length) return;

  function split(el) {
    const text = el.textContent || '';
    el.textContent = '';
    const frag = document.createDocumentFragment();

    [...text].forEach((char, index) => {
      const span = document.createElement('span');
      span.textContent = char;
      span.style.cssText = `
        display: inline-block;
        opacity: 0;
        transform: translateY(100%);
        animation: charReveal 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        animation-delay: ${index * 35}ms;
      `;
      frag.appendChild(span);
    });

    el.appendChild(frag);
  }

  function run() {
    splitTargets.forEach((el) => split(el));
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', run, { once: true });
  } else {
    run();
  }
})();

