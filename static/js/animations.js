(() => {
  const elements = document.querySelectorAll(
    '.reveal, .reveal-stagger, .reveal-left, .reveal-scale'
  );
  if (!elements.length) return;

  const observer = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting) entry.target.classList.add('in-view');
      }
    },
    { threshold: 0.15 }
  );

  elements.forEach((el) => observer.observe(el));
})();

