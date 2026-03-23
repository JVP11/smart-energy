/**
 * Day / Night theme toggle. Persists choice in localStorage.
 */
(function () {
  const key = 'smart-energy-theme';
  const dark = 'dark';
  const light = 'light';

  function getStored() {
    try {
      return localStorage.getItem(key) || light;
    } catch (_) {
      return light;
    }
  }

  function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme === dark ? dark : light);
  }

  function toggle() {
    const current = getStored();
    const next = current === dark ? light : dark;
    try {
      localStorage.setItem(key, next);
    } catch (_) {}
    setTheme(next);
    updateToggleLabel(next);
  }

  function updateToggleLabel(theme) {
    const btn = document.getElementById('themeToggle');
    if (btn) {
      btn.setAttribute('aria-label', theme === dark ? 'Switch to day mode' : 'Switch to night mode');
      btn.textContent = theme === dark ? '☀️' : '🌙';
    }
  }

  // Apply stored theme immediately to avoid flash
  setTheme(getStored());

  // Expose toggle for button clicks
  window.themeToggle = toggle;

  // Update label when DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => updateToggleLabel(getStored()));
  } else {
    updateToggleLabel(getStored());
  }
})();
