/**
 * Mobile Navigation and Responsive Behavior
 * Brain Buddy - Mobile-First Design Implementation
 */

class MobileNavigation {
    constructor() {
        this.isMobile = window.innerWidth < 768;
        this.isTablet = window.innerWidth >= 768 && window.innerWidth < 1024;
        this.isDesktop = window.innerWidth >= 1024;
        
        this.init();
        this.bindEvents();
    }
    
    init() {
        this.createMobileNav();
        this.setupResponsiveClasses();
        this.setupTouchEvents();
        this.optimizeForDevice();
    }
    
    createMobileNav() {
        // Create mobile navigation burger menu
        const navbar = document.querySelector('.navbar');
        if (!navbar) return;
        
        const navToggle = document.createElement('button');
        navToggle.className = 'mobile-nav-toggle d-md-none';
        navToggle.innerHTML = '<i class="fas fa-bars"></i>';
        navToggle.setAttribute('aria-label', 'Toggle navigation');
        
        // Create mobile navigation drawer
        const mobileNav = document.createElement('div');
        mobileNav.className = 'mobile-nav-drawer';
        mobileNav.innerHTML = `
            <div class="mobile-nav-header">
                <h4>Brain Buddy</h4>
                <button class="mobile-nav-close">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <nav class="mobile-nav-content">
                <a href="/" class="mobile-nav-link">
                    <i class="fas fa-home"></i> Home
                </a>
                <a href="/study_index" class="mobile-nav-link">
                    <i class="fas fa-book"></i> Curriculum
                </a>
                <a href="/dashboard?student_id=demo_student" class="mobile-nav-link">
                    <i class="fas fa-chart-bar"></i> Progress
                </a>
                <a href="/study_buddy" class="mobile-nav-link">
                    <i class="fas fa-robot"></i> Study Buddy
                </a>
                <a href="/quick_burst" class="mobile-nav-link">
                    <i class="fas fa-bolt"></i> Quick Burst
                </a>
            </nav>
        `;
        
        // Add overlay
        const overlay = document.createElement('div');
        overlay.className = 'mobile-nav-overlay';
        
        // Insert elements
        navbar.appendChild(navToggle);
        document.body.appendChild(mobileNav);
        document.body.appendChild(overlay);
        
        // Bind navigation events
        this.bindNavEvents(navToggle, mobileNav, overlay);
    }
    
    bindNavEvents(toggle, drawer, overlay) {
        const closeBtn = drawer.querySelector('.mobile-nav-close');
        
        // Open navigation
        toggle.addEventListener('click', () => {
            drawer.classList.add('active');
            overlay.classList.add('active');
            document.body.classList.add('nav-open');
        });
        
        // Close navigation
        const closeNav = () => {
            drawer.classList.remove('active');
            overlay.classList.remove('active');
            document.body.classList.remove('nav-open');
        };
        
        closeBtn.addEventListener('click', closeNav);
        overlay.addEventListener('click', closeNav);
        
        // Close on link click
        drawer.querySelectorAll('.mobile-nav-link').forEach(link => {
            link.addEventListener('click', closeNav);
        });
        
        // Close on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && drawer.classList.contains('active')) {
                closeNav();
            }
        });
    }
    
    setupResponsiveClasses() {
        const body = document.body;
        
        if (this.isMobile) {
            body.classList.add('mobile-device');
            body.classList.remove('tablet-device', 'desktop-device');
        } else if (this.isTablet) {
            body.classList.add('tablet-device');
            body.classList.remove('mobile-device', 'desktop-device');
        } else {
            body.classList.add('desktop-device');
            body.classList.remove('mobile-device', 'tablet-device');
        }
    }
    
    setupTouchEvents() {
        if (!this.isMobile) return;
        
        // Add touch-friendly interactions
        document.querySelectorAll('.btn, .card, .learning-card').forEach(element => {
            element.classList.add('touch-target');
        });
        
        // Implement swipe gestures for lesson navigation
        this.setupSwipeGestures();
    }
    
    setupSwipeGestures() {
        let startX = 0;
        let startY = 0;
        let endX = 0;
        let endY = 0;
        
        document.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
        });
        
        document.addEventListener('touchend', (e) => {
            endX = e.changedTouches[0].clientX;
            endY = e.changedTouches[0].clientY;
            
            const deltaX = endX - startX;
            const deltaY = endY - startY;
            
            // Check if it's a horizontal swipe
            if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 50) {
                if (deltaX > 0) {
                    this.handleSwipeRight();
                } else {
                    this.handleSwipeLeft();
                }
            }
        });
    }
    
    handleSwipeLeft() {
        // Navigate to next learning style or content
        const currentStyle = this.getCurrentLearningStyle();
        const styles = ['visual', 'verbal', 'auditory'];
        const currentIndex = styles.indexOf(currentStyle);
        const nextIndex = (currentIndex + 1) % styles.length;
        
        if (typeof showLearningStyle === 'function') {
            showLearningStyle(styles[nextIndex]);
        }
    }
    
    handleSwipeRight() {
        // Navigate to previous learning style or content
        const currentStyle = this.getCurrentLearningStyle();
        const styles = ['visual', 'verbal', 'auditory'];
        const currentIndex = styles.indexOf(currentStyle);
        const prevIndex = (currentIndex - 1 + styles.length) % styles.length;
        
        if (typeof showLearningStyle === 'function') {
            showLearningStyle(styles[prevIndex]);
        }
    }
    
    getCurrentLearningStyle() {
        const activeContent = document.querySelector('.lesson-content.d-block, .lesson-content:not(.d-none)');
        if (!activeContent) return 'visual';
        
        if (activeContent.id.includes('visual')) return 'visual';
        if (activeContent.id.includes('verbal')) return 'verbal';
        if (activeContent.id.includes('auditory')) return 'auditory';
        return 'visual';
    }
    
    optimizeForDevice() {
        // Optimize images for mobile
        this.optimizeImages();
        
        // Lazy load content for better performance
        this.setupLazyLoading();
        
        // Optimize animations for mobile
        this.optimizeAnimations();
    }
    
    optimizeImages() {
        const images = document.querySelectorAll('img');
        images.forEach(img => {
            if (!img.hasAttribute('loading')) {
                img.setAttribute('loading', 'lazy');
            }
            
            // Add responsive image classes
            if (!img.classList.contains('img-responsive')) {
                img.classList.add('img-responsive');
                img.style.maxWidth = '100%';
                img.style.height = 'auto';
            }
        });
    }
    
    setupLazyLoading() {
        if ('IntersectionObserver' in window) {
            const lazyElements = document.querySelectorAll('.lazy-load');
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('loaded');
                        observer.unobserve(entry.target);
                    }
                });
            });
            
            lazyElements.forEach(element => observer.observe(element));
        }
    }
    
    optimizeAnimations() {
        // Reduce animations on mobile for better performance
        if (this.isMobile) {
            const style = document.createElement('style');
            style.textContent = `
                @media (max-width: 767px) {
                    .mobile-device * {
                        animation-duration: 0.3s !important;
                        transition-duration: 0.2s !important;
                    }
                    
                    .mobile-device .hover-lift:hover {
                        transform: translateY(-2px) !important;
                    }
                }
            `;
            document.head.appendChild(style);
        }
    }
    
    bindEvents() {
        // Handle orientation changes
        window.addEventListener('orientationchange', () => {
            setTimeout(() => {
                this.handleOrientationChange();
            }, 100);
        });
        
        // Handle window resize
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                this.handleResize();
            }, 250);
        });
        
        // Handle viewport changes for mobile browsers
        window.addEventListener('scroll', () => {
            this.handleViewportChange();
        });
    }
    
    handleOrientationChange() {
        // Update device classes
        this.isMobile = window.innerWidth < 768;
        this.isTablet = window.innerWidth >= 768 && window.innerWidth < 1024;
        this.isDesktop = window.innerWidth >= 1024;
        
        this.setupResponsiveClasses();
        
        // Adjust layout for new orientation
        if (this.isMobile) {
            this.adjustMobileLayout();
        }
    }
    
    handleResize() {
        this.handleOrientationChange();
        
        // Update mobile nav visibility
        const mobileToggle = document.querySelector('.mobile-nav-toggle');
        const mobileDrawer = document.querySelector('.mobile-nav-drawer');
        
        if (this.isDesktop && mobileDrawer && mobileDrawer.classList.contains('active')) {
            mobileDrawer.classList.remove('active');
            document.querySelector('.mobile-nav-overlay')?.classList.remove('active');
            document.body.classList.remove('nav-open');
        }
    }
    
    handleViewportChange() {
        // Handle mobile browser viewport changes (address bar hiding/showing)
        if (this.isMobile) {
            const vh = window.innerHeight * 0.01;
            document.documentElement.style.setProperty('--vh', `${vh}px`);
        }
    }
    
    adjustMobileLayout() {
        // Adjust specific mobile layout elements
        const cards = document.querySelectorAll('.learning-card, .card');
        cards.forEach(card => {
            card.style.marginBottom = '1rem';
        });
        
        // Adjust button sizes for mobile
        const buttons = document.querySelectorAll('.btn');
        buttons.forEach(btn => {
            if (!btn.classList.contains('btn-small')) {
                btn.style.minHeight = '48px';
                btn.style.fontSize = '16px'; // Prevent zoom on iOS
            }
        });
    }
}

// Performance optimizations for mobile
class MobilePerformance {
    constructor() {
        this.init();
    }
    
    init() {
        // Preload critical resources
        this.preloadCriticalResources();
        
        // Setup service worker for offline support
        this.setupServiceWorker();
        
        // Optimize scroll performance
        this.optimizeScrolling();
    }
    
    preloadCriticalResources() {
        const criticalResources = [
            '/static/css/mobile-responsive.css',
            '/static/js/profile-corner-new.js'
        ];
        
        criticalResources.forEach(resource => {
            const link = document.createElement('link');
            link.rel = 'prefetch';
            link.href = resource;
            document.head.appendChild(link);
        });
    }
    
    setupServiceWorker() {
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/static/js/sw.js')
                .catch(() => {
                    // Service worker registration failed - this is okay
                });
        }
    }
    
    optimizeScrolling() {
        // Use passive event listeners for better scroll performance
        let scrollTimeout;
        
        document.addEventListener('scroll', () => {
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(() => {
                // Handle scroll end
                this.handleScrollEnd();
            }, 150);
        }, { passive: true });
    }
    
    handleScrollEnd() {
        // Load more content if needed
        const scrollPosition = window.scrollY + window.innerHeight;
        const documentHeight = document.documentElement.scrollHeight;
        
        if (scrollPosition >= documentHeight * 0.8) {
            // Near bottom of page - could trigger lazy loading
            this.triggerLazyLoad();
        }
    }
    
    triggerLazyLoad() {
        const lazyElements = document.querySelectorAll('.lazy-load:not(.loaded)');
        lazyElements.forEach(element => {
            const rect = element.getBoundingClientRect();
            if (rect.top < window.innerHeight + 100) {
                element.classList.add('loaded');
            }
        });
    }
}

// Initialize mobile navigation and performance optimizations
document.addEventListener('DOMContentLoaded', () => {
    new MobileNavigation();
    new MobilePerformance();
});

// Export for use in other modules
window.MobileNavigation = MobileNavigation;
window.MobilePerformance = MobilePerformance;