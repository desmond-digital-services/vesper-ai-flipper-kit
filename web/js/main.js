/**
 * RedWand Landing Page — Interactive JavaScript
 * FAQ accordion, scroll animations, smooth scroll, header effects
 */

(function() {
    'use strict';

    // ==================== SCROLL REVEAL ANIMATION ====================
    function initScrollReveal() {
        // Add reveal class to all major sections automatically
        const sections = document.querySelectorAll('section');
        sections.forEach(function(section, index) {
            section.classList.add('reveal');
            // Stagger the delays for consecutive elements
            const children = section.querySelectorAll('.benefit-card, .audience-card, .included-item, .testimonial-card, .faq-item');
            children.forEach(function(child, childIndex) {
                child.classList.add('reveal');
                child.classList.add('reveal-delay-' + ((childIndex % 4) + 1));
            });
        });
        
        const revealElements = document.querySelectorAll('.reveal');
        
        if (!revealElements.length) return;

        const observerOptions = {
            root: null,
            rootMargin: '0px 0px -80px 0px',
            threshold: 0.1
        };

        const revealObserver = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('revealed');
                    revealObserver.unobserve(entry.target);
                }
            });
        }, observerOptions);

        revealElements.forEach(function(el) {
            revealObserver.observe(el);
        });
    }

    // ==================== FAQ ACCORDION ====================
    function initFAQ() {
        const faqItems = document.querySelectorAll('.faq-item');

        faqItems.forEach(function(item) {
            const button = item.querySelector('.faq-question');
            const answer = item.querySelector('.faq-answer');

            if (!button || !answer) return;

            button.addEventListener('click', function() {
                const isExpanded = button.getAttribute('aria-expanded') === 'true';

                // Close all other items
                faqItems.forEach(function(otherItem) {
                    const otherButton = otherItem.querySelector('.faq-question');
                    const otherAnswer = otherItem.querySelector('.faq-answer');
                    if (otherButton && otherAnswer && otherItem !== item) {
                        otherButton.setAttribute('aria-expanded', 'false');
                        otherAnswer.classList.remove('open');
                    }
                });

                // Toggle current item
                if (isExpanded) {
                    button.setAttribute('aria-expanded', 'false');
                    answer.classList.remove('open');
                } else {
                    button.setAttribute('aria-expanded', 'true');
                    answer.classList.add('open');
                }
            });
        });
    }

    // ==================== SMOOTH SCROLL FOR ANCHOR LINKS ====================
    function initSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
            anchor.addEventListener('click', function(e) {
                const targetId = this.getAttribute('href');
                if (targetId === '#') return;

                const target = document.querySelector(targetId);
                if (target) {
                    e.preventDefault();
                    const headerHeight = document.querySelector('.site-header')?.offsetHeight || 0;
                    const targetPosition = target.getBoundingClientRect().top + window.scrollY - headerHeight - 16;

                    window.scrollTo({
                        top: targetPosition,
                        behavior: 'smooth'
                    });
                }
            });
        });
    }

    // ==================== HEADER SCROLL EFFECT ====================
    function initHeaderScroll() {
        const header = document.querySelector('.site-header');
        if (!header) return;

        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
        }, { passive: true });
    }

    // ==================== VIDEO PREVIEW PLACEHOLDER ====================
    function initVideoPreview() {
        const videoThumb = document.querySelector('.video-thumbnail');
        if (!videoThumb) return;

        videoThumb.addEventListener('click', function() {
            alert('Video preview coming soon! Contact help@redwand.io for a demo.');
        });
    }

    // ==================== STRIPE CHECKOUT ====================
    function initStripeCheckout() {
        // Stripe Payment Link (permanent, no secret key needed on frontend)
        var stripePaymentUrl = 'https://buy.stripe.com/test_eVq14oes6br8cj03aD5Rm0v';

        // All buy/checkout buttons on the page
        var checkoutButtons = document.querySelectorAll('#nav-checkout-btn, #hero-checkout-btn, #stripe-checkout-btn, #included-cta-btn');

        if (!checkoutButtons.length) return;

        checkoutButtons.forEach(function(btn) {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                window.location.href = stripePaymentUrl;
            });
        });
    }

    // ==================== INIT ====================
    function init() {
        initScrollReveal();
        initFAQ();
        initSmoothScroll();
        initHeaderScroll();
        initVideoPreview();
        initStripeCheckout();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
