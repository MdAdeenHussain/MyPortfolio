(() => {
  const preloader = document.getElementById('preloader');
  const nav = document.getElementById('nav');
  const navToggle = document.querySelector('.nav-toggle');
  const navOverlay = document.getElementById('nav-overlay');
  const navOverlayInner = document.querySelector('.nav-overlay-inner');
  const heroProfile = document.querySelector('.hero-profile');

  function setNavScrolled() {
    if (!nav) return;
    nav.classList.toggle('is-scrolled', window.scrollY > 80);
  }

  function closeMenu() {
    if (!nav || !navOverlay || !navToggle) return;
    nav.classList.remove('is-open');
    navOverlay.hidden = true;
    navToggle.setAttribute('aria-expanded', 'false');
    navToggle.setAttribute('aria-label', 'Open menu');
    if (navOverlayInner) navOverlayInner.classList.remove('in-view');
    document.body.style.overflow = '';
  }

  function openMenu() {
    if (!nav || !navOverlay || !navToggle) return;
    nav.classList.add('is-open');
    navOverlay.hidden = false;
    navToggle.setAttribute('aria-expanded', 'true');
    navToggle.setAttribute('aria-label', 'Close menu');
    if (navOverlayInner) navOverlayInner.classList.add('in-view');
    document.body.style.overflow = 'hidden';
  }

  function toggleMenu() {
    if (!nav || !navOverlay) return;
    const isOpen = nav.classList.contains('is-open');
    if (isOpen) closeMenu();
    else openMenu();
  }

  function enableMenu() {
    if (!navToggle) return;
    navToggle.addEventListener('click', toggleMenu);
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') closeMenu();
    });
    document.addEventListener('click', (e) => {
      const t = e.target;
      if (!(t instanceof Element)) return;
      if (t.closest('.nav-overlay-link')) closeMenu();
    });
  }

  function runPreloader() {
    if (!preloader) return Promise.resolve();
    return new Promise((resolve) => {
      const total = 500 + 400 + 400;
      window.setTimeout(() => {
        preloader.classList.add('is-hidden');
        resolve();
      }, total);
    });
  }

  function runHeroSequence() {
    if (heroProfile) {
      window.setTimeout(() => heroProfile.classList.add('is-in'), 100);
    }
  }

  function smoothAnchors() {
    document.addEventListener('click', (e) => {
      const target = e.target;
      if (!(target instanceof Element)) return;
      const link = target.closest('a[href^="#"]');
      if (!link) return;
      const href = link.getAttribute('href') || '';
      const id = href.slice(1);
      const el = document.getElementById(id);
      if (!el) return;
      e.preventDefault();
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });

    const topBtn = document.querySelector('[data-back-to-top="true"]');
    if (topBtn) {
      topBtn.addEventListener('click', () => {
        const hero = document.getElementById('hero');
        if (hero) hero.scrollIntoView({ behavior: 'smooth', block: 'start' });
      });
    }
  }

  function analytics() {
    fetch('/api/analytics/visit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        path: window.location.pathname,
        referrer: document.referrer || '',
      }),
      keepalive: true,
    }).catch(() => {});
  }

  function playgroundParallax() {
    const icons = Array.from(document.querySelectorAll('.playground-icon[data-speed]'));
    if (!icons.length) return;
    const supportsHover = window.matchMedia('(hover: hover)').matches;
    if (!supportsHover) return;

    const state = icons.map((el) => ({
      el,
      speed: Number(el.getAttribute('data-speed') || '0') || 0,
    }));

    document.addEventListener(
      'mousemove',
      (e) => {
        const x = e.clientX / window.innerWidth - 0.5;
        const y = e.clientY / window.innerHeight - 0.5;
        for (const item of state) {
          const tx = x * item.speed * 800;
          const ty = y * item.speed * 800;
          item.el.style.transform = `translate3d(${tx}px, ${ty}px, 0)`;
        }
      },
      { passive: true }
    );
  }

  function init() {
    setNavScrolled();
    window.addEventListener('scroll', setNavScrolled, { passive: true });
    enableMenu();
    smoothAnchors();
    playgroundParallax();

    runPreloader().then(() => {
      document.body.classList.add('is-loaded');
      runHeroSequence();
      window.setTimeout(() => {
        if (preloader) preloader.remove();
      }, 700);
    });

    analytics();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init, { once: true });
  } else {
    init();
  }
})();
