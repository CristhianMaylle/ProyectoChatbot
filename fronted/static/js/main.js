// Funciones comunes para todas las páginas

// Función para mostrar notificaciones
function showNotification(message, type = "info") {
  // Crear elemento de notificación
  const notification = document.createElement("div")
  notification.className = `alert alert-${type} alert-dismissible fade show`
  notification.setAttribute("role", "alert")
  notification.innerHTML = `
    ${message}
    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
  `

  // Contenedor de notificaciones
  let container = document.querySelector(".toast-container")

  // Crear contenedor si no existe
  if (!container) {
    container = document.createElement("div")
    container.className = "toast-container"
    document.body.appendChild(container)
  }

  // Añadir notificación al contenedor
  container.appendChild(notification)

  // Eliminar notificación después de 5 segundos
  setTimeout(() => {
    notification.remove()
  }, 5000)
}

// Función para formatear fechas
function formatDate(dateString) {
  const date = new Date(dateString)
  return date.toLocaleDateString() + " " + date.toLocaleTimeString()
}

// Función para obtener cookies
function getCookie(name) {
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) return parts.pop().split(";").shift()
}

// Inicializar tooltips
document.addEventListener("DOMContentLoaded", () => {
  // Inicializar tooltips de Bootstrap
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
  tooltipTriggerList.map((tooltipTriggerEl) => new bootstrap.Tooltip(tooltipTriggerEl))
})

// Función para manejar errores de fetch
async function handleFetchResponse(response) {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    const errorMessage = errorData.detail || `Error ${response.status}: ${response.statusText}`
    throw new Error(errorMessage)
  }
  return response.json()
}
