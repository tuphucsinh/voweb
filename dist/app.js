(() => {
  const menuButton = document.querySelector('.menu-toggle');
  const nav = document.querySelector('.primary-nav');
  if (menuButton && nav) {
    menuButton.addEventListener('click', () => {
      const next = menuButton.getAttribute('aria-expanded') !== 'true';
      menuButton.setAttribute('aria-expanded', String(next));
      nav.classList.toggle('is-open', next);
      document.body.classList.toggle('menu-open', next);
    });
    nav.querySelectorAll('a').forEach(a => a.addEventListener('click', () => {
      menuButton.setAttribute('aria-expanded', 'false');
      nav.classList.remove('is-open');
      document.body.classList.remove('menu-open');
    }));
  }

  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  const header = document.querySelector('.site-header');
  const hero = document.querySelector('.hero');
  const heroCopy = document.querySelector('.hero-copy');
  const heroImage = document.querySelector('.hero-visual img');
  let ticking = false;
  const onScrollPremium = () => {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => {
      const y = window.scrollY || 0;
      if (header) header.classList.toggle('is-scrolled', y > 12);
      if (!reduced && hero && y < hero.offsetHeight + 140) {
        const p = Math.min(1, y / Math.max(1, hero.offsetHeight));
        if (heroCopy) heroCopy.style.setProperty('--hero-copy-shift', `${p * -8}px`);
        if (heroImage) heroImage.style.setProperty('--hero-image-shift', `${p * 14}px`);
      }
      ticking = false;
    });
  };
  window.addEventListener('scroll', onScrollPremium, { passive: true });
  onScrollPremium();

  if (!reduced && 'IntersectionObserver' in window) {
    const revealObserver = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          revealObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.10, rootMargin: '0px 0px -24px 0px' });
    document.querySelectorAll('.reveal').forEach(el => revealObserver.observe(el));
  } else {
    document.querySelectorAll('.reveal').forEach(el => el.classList.add('is-visible'));
  }

  // Approved transition spec: subtle cream darkening + sunset bleed + bronze rule fade.
  const why = document.querySelector('.why-partner');
  const market = document.querySelector('.market');
  const rule = document.querySelector('.transition-rule');
  if (why && market && 'IntersectionObserver' in window) {
    const transitionObserver = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        const active = entry.isIntersecting;
        market.classList.toggle('is-near', active);
        why.classList.toggle('approaching-dark', active);
        if (rule) {
          rule.style.opacity = active ? '.35' : '1';
          rule.style.transform = active ? 'scaleX(.72)' : 'scaleX(1)';
        }
      });
    }, { threshold: 0.02, rootMargin: '90px 0px 35% 0px' });
    transitionObserver.observe(market);
  }

  document.querySelectorAll('[data-lead-form]').forEach(form => {
    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      const status = form.querySelector('.form-status');
      const submit = form.querySelector('[type="submit"]');
      const data = Object.fromEntries(new FormData(form).entries());
      data.form_type = form.dataset.leadForm;
      const en = document.documentElement.lang === 'en';
      if (status) status.textContent = en ? 'Sending…' : 'Đang gửi…';
      if (submit) submit.disabled = true;
      try {
        const response = await fetch('/api/lead', {
          method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(data)
        });
        const result = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(result.error || 'submit_failed');
        form.reset();
        if (window.turnstile) { try { window.turnstile.reset(); } catch (_) {} }
        if (status) status.textContent = en ? 'Thank you. Your message has been received.' : 'Cảm ơn. VOrigin đã nhận được thông tin của bạn.';
      } catch (_) {
        if (status) status.textContent = en ? 'Unable to send right now. Please try again later.' : 'Hiện chưa thể gửi. Vui lòng thử lại sau.';
      } finally {
        if (submit) submit.disabled = false;
      }
    });
  });
})();
