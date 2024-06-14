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

/**
 * Close a toast.
 *
 * @type {Element} element
 */
function closeToast(element) {
  const toast = element.closest(".app-toast");
  console.debug("Closing toast", { element, toast });
  toast.remove();
  // toast.classList.add("app-fade-out")
}

/**
 * Switch between tabs.
 * Containing element must have the 'x-tabs' class.
 * Tab content must have the 'x-tab' class.
 */
function switchTab(element, newTabSelector) {
  const container = element.closest(".x-tabs-container");

  // Remove .is-active from all tabs
  container.querySelector(".tabs").querySelectorAll("li").forEach((li) => li.classList.remove("is-active"));

  // Add .is-active to the clicked tab
  element.classList.add("is-active");

  // Hide all tab content
  container.querySelectorAll(".x-tab-content").forEach((e) => e.setAttribute("hidden", ""));

  // Display the selected tab content
  container.querySelector(newTabSelector).removeAttribute("hidden");
}

// function initBulmaFileInputs() {
//   console.debug("Configuring Bulma file inputs");
//   document.querySelectorAll(".file").forEach((element) => {
//     const fileInput = element.querySelector(".file-input");
//     const fileName = element.querySelector(".file-name");
//     console.debug("Configuring file input", fileInput.attributes.getNamedItem("name").value, element);
//     fileInput.onchange = () => {
//       if (fileInput.files.length > 0) {
//         fileName.textContent = fileInput.files[0].name;
//       }
//     };
//   });
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
