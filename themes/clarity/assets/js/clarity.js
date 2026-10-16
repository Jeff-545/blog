(() => {
  const key = 'clarity-color-scheme';
  const root = document.documentElement;
  const preference = window.matchMedia('(prefers-color-scheme: light)');
  const savedTheme = () => {
    try { return localStorage.getItem(key); } catch { return null; }
  };
  const apply = (theme) => {
    root.dataset.theme = theme;
    const button = document.querySelector('.theme-toggle');
    if (button) {
      const label = theme === 'dark' ? '切换到浅色模式' : '切换到深色模式';
      button.setAttribute('aria-label', label);
      button.title = label;
    }
  };
  const systemTheme = () => preference.matches ? 'light' : 'dark';
  const initial = savedTheme();
  apply(initial === 'light' || initial === 'dark' ? initial : systemTheme());
  document.addEventListener('DOMContentLoaded', () => {
    const button = document.querySelector('.theme-toggle');
    if (!button) return;
    apply(root.dataset.theme);
    button.hidden = false;
    button.addEventListener('click', () => {
      const theme = root.dataset.theme === 'dark' ? 'light' : 'dark';
      apply(theme);
      try { localStorage.setItem(key, theme); } catch { /* Storage is optional. */ }
    });
  });
  preference.addEventListener('change', () => {
    const saved = savedTheme();
    if (saved !== 'light' && saved !== 'dark') apply(systemTheme());
  });
})();
