/** ========================================
 * MAIN JAVASCRIPT
 * Navigation, utilities, and initialization
 * ===================================== */

(function() {
  'use strict';

  /**
   * Navigation functionality
   */
  const Navigation = {
    init() {
      this.setupSmoothScroll();
      this.setupProgressBar();
      this.setupSectionNav();
      this.setupMobileNav();
      this.updateActiveNav();
    },

    setupSmoothScroll() {
      document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
          e.preventDefault();
          const target = document.querySelector(this.getAttribute('href'));
          if (target) {
            target.scrollIntoView({
              behavior: 'smooth',
              block: 'start'
            });
          }
        });
      });
    },

    setupProgressBar() {
      const progressBar = document.querySelector('.progress-indicator-bar');
      if (!progressBar) return;

      window.addEventListener('scroll', () => {
        const scrollTop = window.scrollY;
        const docHeight = document.documentElement.scrollHeight - window.innerHeight;
        const progress = (scrollTop / docHeight) * 100;
        progressBar.style.width = `${progress}%`;
      });
    },

    setupSectionNav() {
      const upBtn = document.querySelector('.nav-arrow.up');
      const downBtn = document.querySelector('.nav-arrow.down');
      const sections = document.querySelectorAll('.lesson-section');

      if (!sections.length) return;

      const getCurrentSection = () => {
        const scrollPos = window.scrollY + window.innerHeight / 2;
        let current = sections[0];
        
        sections.forEach(section => {
          if (section.offsetTop <= scrollPos) {
            current = section;
          }
        });
        
        return current;
      };

      if (upBtn) {
        upBtn.addEventListener('click', () => {
          const current = getCurrentSection();
          const prev = current.previousElementSibling;
          if (prev && prev.classList.contains('lesson-section')) {
            prev.scrollIntoView({ behavior: 'smooth' });
          } else {
            window.scrollTo({ top: 0, behavior: 'smooth' });
          }
        });
      }

      if (downBtn) {
        downBtn.addEventListener('click', () => {
          const current = getCurrentSection();
          const next = current.nextElementSibling;
          if (next && next.classList.contains('lesson-section')) {
            next.scrollIntoView({ behavior: 'smooth' });
          }
        });
      }
    },

    setupMobileNav() {
      const tocToggle = document.querySelector('.toc-toggle');
      const tocSidebar = document.querySelector('.toc-sidebar');

      if (tocToggle && tocSidebar) {
        tocToggle.addEventListener('click', () => {
          tocSidebar.classList.toggle('open');
        });

        // Close on outside click
        document.addEventListener('click', (e) => {
          if (!tocSidebar.contains(e.target) && !tocToggle.contains(e.target)) {
            tocSidebar.classList.remove('open');
          }
        });
      }
    },

    updateActiveNav() {
      const sections = document.querySelectorAll('.lesson-section[id]');
      const navLinks = document.querySelectorAll('.toc-link');

      if (!sections.length || !navLinks.length) return;

      window.addEventListener('scroll', () => {
        const scrollPos = window.scrollY + 100;

        sections.forEach(section => {
          const top = section.offsetTop;
          const height = section.offsetHeight;
          const id = section.getAttribute('id');

          if (scrollPos >= top && scrollPos < top + height) {
            navLinks.forEach(link => {
              link.classList.remove('active');
              if (link.getAttribute('href') === `#${id}`) {
                link.classList.add('active');
              }
            });
          }
        });
      });
    }
  };

  /**
   * Syntax highlighting utility
   */
  const SyntaxHighlighter = {
    init() {
      document.querySelectorAll('pre code').forEach(block => {
        this.highlight(block);
      });
    },

    highlight(element) {
      let html = element.innerHTML;
      
      // Escape HTML entities first
      html = html.replace(/&/g, '&amp;')
                 .replace(/</g, '&lt;')
                 .replace(/>/g, '&gt;');

      // HTML highlighting
      if (element.classList.contains('language-html')) {
        html = this.highlightHTML(html);
      }
      // CSS highlighting
      else if (element.classList.contains('language-css')) {
        html = this.highlightCSS(html);
      }
      // JS highlighting
      else if (element.classList.contains('language-js') || 
               element.classList.contains('language-javascript')) {
        html = this.highlightJS(html);
      }

      element.innerHTML = html;
    },

    highlightHTML(html) {
      // Comments
      html = html.replace(/(&lt;!--[\s\S]*?--&gt;)/g, '<span class="comment">$1</span>');
      // Tags
      html = html.replace(/(&lt;\/?)([\w-]+)/g, '$1<span class="tag">$2</span>');
      // Attributes
      html = html.replace(/(\s)([\w-]+)(=)/g, '$1<span class="attr-name">$2</span>$3');
      // Strings
      html = html.replace(/("[^"]*")/g, '<span class="string">$1</span>');
      return html;
    },

    highlightCSS(html) {
      // Comments
      html = html.replace(/(\/\*[\s\S]*?\*\/)/g, '<span class="comment">$1</span>');
      // Selectors
      html = html.replace(/^([^{]+)/gm, '<span class="selector">$1</span>');
      // Properties
      html = html.replace(/([\w-]+)(\s*:)/g, '<span class="property">$1</span>$2');
      // Values
      html = html.replace(/:\s*([^;]+)/g, ': <span class="string">$1</span>');
      return html;
    },

    highlightJS(html) {
      // Comments
      html = html.replace(/(\/\/.*$)/gm, '<span class="comment">$1</span>');
      html = html.replace(/(\/\*[\s\S]*?\*\/)/g, '<span class="comment">$1</span>');
      // Keywords
      const keywords = /\b(const|let|var|function|return|if|else|for|while|class|import|export|from|async|await|try|catch|new|this|true|false|null|undefined)\b/g;
      html = html.replace(keywords, '<span class="keyword">$1</span>');
      // Strings
      html = html.replace(/('[^']*'|"[^"]*"|`[^`]*`)/g, '<span class="string">$1</span>');
      // Functions
      html = html.replace(/(\w+)(\s*\()/g, '<span class="function">$1</span>$2');
      // Numbers
      html = html.replace(/\b(\d+)\b/g, '<span class="number">$1</span>');
      return html;
    }
  };

  /**
   * Intersection Observer for animations
   */
  const ScrollAnimations = {
    init() {
      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add('animate-in');
          }
        });
      }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
      });

      document.querySelectorAll('.animate-on-scroll').forEach(el => {
        observer.observe(el);
      });
    }
  };

  /**
   * Utility functions
   */
  const Utils = {
    // Debounce function
    debounce(func, wait) {
      let timeout;
      return function executedFunction(...args) {
        const later = () => {
          clearTimeout(timeout);
          func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
      };
    },

    // Throttle function
    throttle(func, limit) {
      let inThrottle;
      return function(...args) {
        if (!inThrottle) {
          func.apply(this, args);
          inThrottle = true;
          setTimeout(() => inThrottle = false, limit);
        }
      };
    },

    // Copy to clipboard
    async copyToClipboard(text) {
      try {
        await navigator.clipboard.writeText(text);
        return true;
      } catch (err) {
        // Fallback
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        return true;
      }
    },

    // Format code
    formatCode(code, language) {
      // Simple indentation fix
      return code.replace(/^\s+/gm, '');
    }
  };

  // Initialize everything when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  function init() {
    Navigation.init();
    SyntaxHighlighter.init();
    ScrollAnimations.init();
    
    // Expose utilities globally
    window.WebDevUtils = Utils;
  }
})();
