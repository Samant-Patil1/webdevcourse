/** ========================================
 * THEME TOGGLE SYSTEM
 * Complete Dark/Light theme implementation
 * ===================================== */

(function() {
  'use strict';

  // Theme configuration
  const THEME_KEY = 'webdev-course-theme';
  const THEMES = {
    DARK: 'dark',
    LIGHT: 'light'
  };

  /**
   * Initialize theme system
   */
  function initTheme() {
    const savedTheme = localStorage.getItem(THEME_KEY);
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    // Default to dark if no saved preference
    const initialTheme = savedTheme || (systemPrefersDark ? THEMES.DARK : THEMES.LIGHT);
    
    applyTheme(initialTheme);
    setupThemeToggle();
    setupSystemPreferenceListener();
  }

  /**
   * Apply theme to document
   */
  function applyTheme(theme) {
    if (theme === THEMES.LIGHT) {
      document.documentElement.setAttribute('data-theme', 'light');
    } else {
      document.documentElement.removeAttribute('data-theme');
    }
    
    // Update toggle button state
    const toggle = document.querySelector('.theme-toggle');
    if (toggle) {
      toggle.setAttribute('aria-pressed', theme === THEMES.LIGHT);
      toggle.setAttribute('aria-label', `Switch to ${theme === THEMES.LIGHT ? 'dark' : 'light'} mode`);
    }
    
    // Save preference
    localStorage.setItem(THEME_KEY, theme);
    
    // Dispatch custom event
    window.dispatchEvent(new CustomEvent('themechange', { detail: { theme } }));
  }

  /**
   * Toggle between themes
   */
  function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme') === 'light' 
      ? THEMES.LIGHT 
      : THEMES.DARK;
    const newTheme = currentTheme === THEMES.DARK ? THEMES.LIGHT : THEMES.DARK;
    
    applyTheme(newTheme);
  }

  /**
   * Setup theme toggle button
   */
  function setupThemeToggle() {
    const toggle = document.querySelector('.theme-toggle');
    if (!toggle) return;
    
    toggle.addEventListener('click', toggleTheme);
    
    // Keyboard support
    toggle.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        toggleTheme();
      }
    });
  }

  /**
   * Listen for system preference changes
   */
  function setupSystemPreferenceListener() {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    
    mediaQuery.addEventListener('change', (e) => {
      // Only auto-switch if user hasn't manually set preference
      if (!localStorage.getItem(THEME_KEY)) {
        applyTheme(e.matches ? THEMES.DARK : THEMES.LIGHT);
      }
    });
  }

  /**
   * Get current theme
   */
  function getCurrentTheme() {
    return document.documentElement.getAttribute('data-theme') === 'light' 
      ? THEMES.LIGHT 
      : THEMES.DARK;
  }

  /**
   * Check if dark mode is active
   */
  function isDarkMode() {
    return getCurrentTheme() === THEMES.DARK;
  }

  // Expose to global scope
  window.ThemeManager = {
    init: initTheme,
    toggle: toggleTheme,
    apply: applyTheme,
    getCurrent: getCurrentTheme,
    isDark: isDarkMode,
    THEMES
  };

  // Auto-initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initTheme);
  } else {
    initTheme();
  }
})();
