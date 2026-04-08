/**
 * Vesper AI Landing Page — Interactive JavaScript
 * Minimal: FAQ accordion only
 */

(function() {
    'use strict';

    // ==================== FAQ ACCORDION ====================
    function initFAQ() {
        const faqItems = document.querySelectorAll('.faq-item');

        faqItems.forEach(function(item) {
            const button = item.querySelector('.faq-question');
            const answer = item.querySelector('.faq-answer');

            if (!button || !answer) return;

            button.addEventListener('click', function() {
                const isExpanded = button.getAttribute('aria-expanded') === 'true';

                // Close all other items (optional: remove for multi-open behavior)
                faqItems.forEach(function(otherItem) {
                    const otherButton = otherItem.querySelector('.faq-question');
                    const otherAnswer = otherItem.querySelector('.faq-answer');
                    if (otherButton && otherAnswer && otherItem !== item) {
                        otherButton.setAttribute('aria-expanded', 'false');
                        otherAnswer.hidden = true;
                    }
                });

                // Toggle current item
                if (isExpanded) {
                    button.setAttribute('aria-expanded', 'false');
                    answer.hidden = true;
                } else {
                    button.setAttribute('aria-expanded', 'true');
                    answer.hidden = false;
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

        let lastScrollY = 0;

        window.addEventListener('scroll', function() {
            const scrollY = window.scrollY;

            if (scrollY > 100) {
                header.style.boxShadow = '0 4px 20px rgba(0,0,0,0.3)';
            } else {
                header.style.boxShadow = 'none';
            }

            lastScrollY = scrollY;
        }, { passive: true });
    }

    // ==================== STRIPE CHECKOUT HANDLER ====================
    // STRIPE_INTEGRATION_POINT: Replace with your actual Stripe product/price ID
    // Example: const stripe = Stripe('pk_live_YOUR_PUBLISHABLE_KEY');
    //
    // function redirectToStripeCheckout() {
    //     stripe.redirectToCheckout({
    //         lineItems: [{ price: 'price_YOUR_PRICE_ID', quantity: 1 }],
    //         mode: 'payment',
    //         successUrl: window.location.origin + '/success',
    //         cancelUrl: window.location.origin + '/cancel',
    //     }).catch(function(err) {
    //         console.error('Stripe checkout error:', err);
    //     });
    // }
    //
    // document.querySelectorAll('[id*="checkout"]').forEach(function(btn) {
    //     btn.addEventListener('click', function(e) {
    //         if (this.tagName === 'A') {
    //             // Let anchor work normally for now (href="#checkout")
    //             return;
    //         }
    //         e.preventDefault();
    //         redirectToStripeCheckout();
    //     });
    // });

    // ==================== VIDEO PREVIEW PLACEHOLDER ====================
    function initVideoPreview() {
        const videoThumb = document.querySelector('.video-thumbnail');
        if (!videoThumb) return;

        videoThumb.addEventListener('click', function() {
            // Placeholder: Replace with actual video modal or redirect
            alert('Video preview coming soon! Contact help@vespere.ai for a demo.');
        });
    }

    // ==================== INIT ====================
    function init() {
        initFAQ();
        initSmoothScroll();
        initHeaderScroll();
        initVideoPreview();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
