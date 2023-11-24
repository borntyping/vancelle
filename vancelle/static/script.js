/**
 * Close a modal by finding the .app-htmx-modal element and removing it, then
 * restoring the page's original URL as the HTMX responses that created the
 * modal may have changed the URL.
 *
 * @type {Element} element
 * @type {onclick} event
 * @type {string} selector
 * */
function closeHtmxModal(element, event, selector = '.app-htmx-modal') {
    const modal = element.closest(selector)
    console.debug("Closing modal", {element, selector, modal})
    modal.remove()
    event.stopPropagation()
}

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
