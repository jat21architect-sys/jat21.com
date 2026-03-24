/* Jeannot Tsirenge Portfolio — main.js */

(() => {
  'use strict';

  // ---------------------------------------------------------
  // Header scroll behaviour
  // ---------------------------------------------------------
  const header = document.getElementById('site-header');
  if (header) {
    const onScroll = () => {
      header.classList.toggle('scrolled', window.scrollY > 60);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll(); // initial
  }

  // ---------------------------------------------------------
  // Mobile nav toggle
  // ---------------------------------------------------------
  const toggle = document.querySelector('.nav__toggle');
  const navLinks = document.querySelector('.nav__links');

  if (toggle && navLinks) {
    // Escape handler — added on open, removed on close so it never leaks
    const onEscape = e => {
      if (e.key === 'Escape') {
        closeMenu();
        toggle.focus();
      }
    };

    const openMenu = () => {
      navLinks.classList.add('is-open');
      toggle.classList.add('is-open');
      toggle.setAttribute('aria-expanded', 'true');
      document.body.style.overflow = 'hidden';
      // Disable backdrop-filter on header so the fixed overlay fills the
      // viewport on Safari/iOS (backdrop-filter containment bug)
      header?.classList.add('nav-open');
      navLinks.querySelector('a')?.focus();
      document.addEventListener('keydown', onEscape);
    };

    const closeMenu = () => {
      navLinks.classList.remove('is-open');
      toggle.classList.remove('is-open');
      toggle.setAttribute('aria-expanded', 'false');
      document.body.style.overflow = '';
      header?.classList.remove('nav-open');
      document.removeEventListener('keydown', onEscape);
    };

    // Sync aria-expanded from real DOM state on init (handles bfcache restores)
    toggle.setAttribute('aria-expanded', String(navLinks.classList.contains('is-open')));

    toggle.addEventListener('click', () => {
      navLinks.classList.contains('is-open') ? closeMenu() : openMenu();
    });

    // Close on link click
    navLinks.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', closeMenu);
    });

    // Close when viewport crosses into desktop — prevents stuck scroll lock
    // on device rotation or DevTools breakpoint crossing
    const mq = window.matchMedia('(max-width: 768px)');
    const onBreakpoint = e => {
      if (!e.matches) closeMenu();
    };
    mq.addEventListener('change', onBreakpoint);
  }

  // ---------------------------------------------------------
  // Scroll reveal
  // ---------------------------------------------------------
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(
      entries => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible');
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: '0px 0px -40px 0px' }
    );

    document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
  } else {
    // Fallback: show all immediately
    document.querySelectorAll('.reveal').forEach(el => el.classList.add('is-visible'));
  }

  // ---------------------------------------------------------
  // Testimonial rotator
  // ---------------------------------------------------------
  const track = document.querySelector('.testimonials-track');
  if (track) {
    const testimonials = Array.from(track.querySelectorAll('.testimonial'));
    if (testimonials.length > 1) {
      let current = 0;
      const show = idx => {
        testimonials[current].classList.add('testimonial--hidden');
        current = (idx + testimonials.length) % testimonials.length;
        testimonials[current].classList.remove('testimonial--hidden');
      };
      setInterval(() => show(current + 1), 5500);
    }
  }

  // ---------------------------------------------------------
  // Category filter — preserve scroll position on page load
  // ---------------------------------------------------------
  const filterBar = document.querySelector('.filter-bar__nav');
  if (filterBar) {
    const active = filterBar.querySelector('.filter-btn--active');
    if (active) {
      active.scrollIntoView({ block: 'nearest', inline: 'center' });
    }
  }

})();
