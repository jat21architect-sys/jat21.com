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
    let ignoreToggleClick = false;
    let keyboardToggleKey = null;
    const menuItems = () => Array.from(navLinks.querySelectorAll('a'));
    const focusFirstMenuLink = () => {
      window.setTimeout(() => {
        menuItems()[0]?.focus();
      }, 80);
    };

    const onMenuKeydown = e => {
      if (e.key === 'Escape') {
        closeMenu({ restoreFocus: true });
        return;
      }

      if (e.key !== 'Tab' || !navLinks.classList.contains('is-open')) {
        return;
      }

      const links = menuItems();
      if (!links.length) {
        return;
      }

      const firstLink = links[0];
      const lastLink = links[links.length - 1];
      const current = document.activeElement;

      if (current === toggle) {
        e.preventDefault();
        (e.shiftKey ? lastLink : firstLink)?.focus();
        return;
      }

      if (e.shiftKey && current === firstLink) {
        e.preventDefault();
        toggle.focus();
        return;
      }

      if (!e.shiftKey && current === lastLink) {
        e.preventDefault();
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
      focusFirstMenuLink();
      document.addEventListener('keydown', onMenuKeydown);
    };

    const closeMenu = ({ restoreFocus = false } = {}) => {
      navLinks.classList.remove('is-open');
      toggle.classList.remove('is-open');
      toggle.setAttribute('aria-expanded', 'false');
      document.body.style.overflow = '';
      header?.classList.remove('nav-open');
      document.removeEventListener('keydown', onMenuKeydown);
      if (restoreFocus) {
        toggle.focus();
      }
    };

    // Sync aria-expanded from real DOM state on init (handles bfcache restores)
    toggle.setAttribute('aria-expanded', String(navLinks.classList.contains('is-open')));

    toggle.addEventListener('keydown', e => {
      if (e.key !== 'Enter' && e.key !== ' ') {
        return;
      }

      e.preventDefault();
      keyboardToggleKey = e.key;
    });

    toggle.addEventListener('keyup', e => {
      if (!keyboardToggleKey || e.key !== keyboardToggleKey) {
        return;
      }

      e.preventDefault();
      ignoreToggleClick = true;
      keyboardToggleKey = null;
      navLinks.classList.contains('is-open')
        ? closeMenu({ restoreFocus: true })
        : openMenu();
    });

    toggle.addEventListener('click', () => {
      if (ignoreToggleClick) {
        ignoreToggleClick = false;
        return;
      }

      navLinks.classList.contains('is-open') ? closeMenu() : openMenu();
    });

    // Close on link click
    navLinks.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', closeMenu);
    });

    // Close when viewport crosses into desktop — prevents stuck scroll lock
    // on device rotation or DevTools breakpoint crossing
    const mq = window.matchMedia('(max-width: 767px)');
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

  // ---------------------------------------------------------
  // Form submit state
  // ---------------------------------------------------------
  document.querySelectorAll('form[data-submit-pending-label]').forEach(form => {
    form.addEventListener('submit', () => {
      const submitButton = form.querySelector('button[type="submit"], input[type="submit"]');
      if (!submitButton || submitButton.disabled) {
        return;
      }

      submitButton.dataset.originalLabel = submitButton.textContent;
      submitButton.textContent = form.dataset.submitPendingLabel;
      submitButton.disabled = true;
      submitButton.setAttribute('aria-disabled', 'true');
    });
  });

})();
