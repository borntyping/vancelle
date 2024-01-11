/**
 * Close a toast.
 *
 * @type {Element} element
 */
function closeToast(element) {
    const toast = element.closest('.app-toast')
    console.debug("Closing toast", {element, toast})
    toast.remove()
    // toast.classList.add("app-fade-out")
}

/**
 * Switch between tabs.
 * Containing element must have the 'x-tabs' class.
 * Tab content must have the 'x-tab' class.
 */
function switchTab(element, newTabSelector) {
  const container = element.closest('.x-tabs-container')

  // Remove .is-active from all tabs
  container.querySelector('.tabs').querySelectorAll('li').forEach((li) => li.classList.remove("is-active"))

  // Add .is-active to the clicked tab
  element.classList.add('is-active')

  // Hide all tab content
  container.querySelectorAll('.x-tab-content').forEach((e) => e.setAttribute('hidden', ''))

  // Display the selected tab content
  container.querySelector(newTabSelector).removeAttribute('hidden')
}

/**
 * @type {Element} element
 */
function initBulmaFileInput(element){
  const fileInput = element.querySelector('.file-input')
  const fileName = element.querySelector('.file-name')
  console.debug('Configuring file input', fileInput.attributes.getNamedItem('name').value, element)
  fileInput.onchange = () => {
      if (fileInput.files.length > 0) {
        fileName.textContent = fileInput.files[0].name;
      }
  }
}

window.onload = () => {
  console.debug('Configuring Bulma file inputs')
  document.querySelectorAll('.file').forEach(initBulmaFileInput)
}
