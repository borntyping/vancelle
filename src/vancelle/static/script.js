const THEME_ATTRIBUTE = "data-bs-theme";

/**
 * Set the current theme using Bulma's data-theme attribute,
 * and record it in localStorage.
 */
function setTheme(theme) {
  console.debug(`Setting theme to ${theme}, page will use configured theme`);
  document.querySelector("html").setAttribute(THEME_ATTRIBUTE, theme);
  localStorage.setItem("theme", theme);
}

/**
 * Clear Bulma's data-theme attribute and the theme in localStorage.
 */
function clearTheme() {
  console.debug("Clearing theme, page will use the system theme");
  document.querySelector("html").removeAttribute(THEME_ATTRIBUTE);
  localStorage.removeItem("theme");
}

/**
 * Toggle the current theme.
 */
function toggleTheme(event) {
  event.preventDefault();
  const theme = document.querySelector("html").getAttribute(THEME_ATTRIBUTE);
  const systemLight = window.matchMedia("(prefers-color-scheme: light)").matches;
  const systemDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  if (systemLight) {
    theme === "dark" ? clearTheme() : setTheme('dark');
  } else if (systemDark) {
    theme === "light" ? clearTheme() : setTheme('light');
  } else {
    theme === "dark" ? setTheme("dark") : setTheme('light');
  }
}

/**
 * Set Bulma's data-theme attribute from a theme stored in localStorage,
 * then configure elements we can click on to toggle the theme.
 */
function initTheme() {
  console.debug("Configuring theme toggles");
  const storedTheme = localStorage.getItem("theme");
  if (storedTheme !== null) {
    document.querySelector("html").setAttribute(THEME_ATTRIBUTE, storedTheme);
  }
  document.querySelectorAll("[data-theme-toggle]").forEach((element) => {
    element.addEventListener("click", toggleTheme);
  });
}

// /**
//  * Close a toast.
//  *
//  * @type {Element} element
//  */
// function closeToast(element) {
//   const toast = element.closest(".app-toast");
//   console.debug("Closing toast", { element, toast });
//   toast.remove();
//   // toast.classList.add("app-fade-out")
// }

function initBootstrapPopovers() {
  console.debug("Configuring Bootstrap popovers");
  const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]')
  const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl, {}))
}

window.onload = () => {
  initTheme();
  initBootstrapPopovers();
};
