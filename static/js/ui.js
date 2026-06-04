/**
 * MedSystem PRO - UI Utility Functions
 * Provides toast notifications, modals, formatters, and loading indicators
 */

// ============================================================================
// TOAST NOTIFICATIONS
// ============================================================================

/**
 * Display a temporary toast notification
 * @param {string} message - Notification message
 * @param {string} type - Notification type: 'info', 'success', 'error', 'warning'
 * @param {number} duration - Duration in milliseconds (default: 3000)
 */
function showToast(message, type = 'info', duration = 3000) {
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  
  // Add toast container if it doesn't exist
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.style.position = 'fixed';
    container.style.top = '20px';
    container.style.right = '20px';
    container.style.zIndex = '9999';
    container.style.maxWidth = '400px';
    document.body.appendChild(container);
  }
  
  container.appendChild(toast);
  
  setTimeout(() => {
    toast.style.transition = 'opacity 0.3s ease-out';
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

// ============================================================================
// MODAL DIALOGS
// ============================================================================

/**
 * Display a dynamic modal dialog
 * @param {string} title - Modal title
 * @param {string|HTMLElement} content - Modal content
 * @param {Array} buttons - Array of button objects: { text, onclick, style }
 * @param {boolean} includeClose - Include close button (default: true)
 * @returns {Promise} Promise that resolves when a button is clicked
 */
function showModal(title, content, buttons = [], includeClose = true) {
  return new Promise((resolve) => {
    // Create backdrop
    const backdrop = document.createElement('div');
    backdrop.className = 'modal-backdrop';
    backdrop.style.display = 'block';

    // Create modal container
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.style.display = 'block';

    // Create modal dialog
    const dialog = document.createElement('div');
    dialog.className = 'modal-dialog';

    // Create modal content
    const modalContent = document.createElement('div');
    modalContent.className = 'modal-content';

    // Header
    const header = document.createElement('div');
    header.className = 'modal-header';

    const titleEl = document.createElement('h5');
    titleEl.className = 'modal-title';
    titleEl.textContent = title;
    header.appendChild(titleEl);

    if (includeClose) {
      const closeBtn = document.createElement('button');
      closeBtn.type = 'button';
      closeBtn.className = 'btn-close';
      closeBtn.setAttribute('aria-label', 'Close');
      closeBtn.innerHTML = '&times;';
      closeBtn.onclick = () => {
        backdrop.remove();
        modal.remove();
        resolve(null);
      };
      header.appendChild(closeBtn);
    }

    // Body
    const body = document.createElement('div');
    body.className = 'modal-body';
    if (typeof content === 'string') {
      body.innerHTML = content;
    } else {
      body.appendChild(content);
    }

    // Footer with buttons
    const footer = document.createElement('div');
    footer.className = 'modal-footer';

    if (buttons.length === 0) {
      // Default close button if no buttons provided
      const closeBtn = document.createElement('button');
      closeBtn.type = 'button';
      closeBtn.className = 'btn btn-secondary';
      closeBtn.textContent = 'Close';
      closeBtn.onclick = () => {
        backdrop.remove();
        modal.remove();
        resolve(null);
      };
      footer.appendChild(closeBtn);
    } else {
      buttons.forEach((btn) => {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = `btn btn-${btn.style || 'primary'}`;
        button.textContent = btn.text;
        button.onclick = () => {
          backdrop.remove();
          modal.remove();
          if (btn.onclick) btn.onclick();
          resolve(btn.text);
        };
        footer.appendChild(button);
      });
    }

    // Assemble modal
    modalContent.appendChild(header);
    modalContent.appendChild(body);
    modalContent.appendChild(footer);
    dialog.appendChild(modalContent);
    modal.appendChild(dialog);

    // Add to DOM
    document.body.appendChild(backdrop);
    document.body.appendChild(modal);

    // Close on backdrop click
    backdrop.onclick = () => {
      backdrop.remove();
      modal.remove();
      resolve(null);
    };

    // Prevent closing when clicking inside modal
    modal.onclick = (e) => {
      if (e.target === modal) {
        e.stopPropagation();
      }
    };
  });
}

// ============================================================================
// CONFIRM DIALOG
// ============================================================================

/**
 * Display a confirmation dialog
 * @param {string} title - Dialog title
 * @param {string} message - Confirmation message
 * @returns {Promise<boolean>} Resolves to true if confirmed, false if cancelled
 */
function confirmAction(title, message) {
  return new Promise((resolve) => {
    const buttons = [
      {
        text: 'Cancel',
        onclick: () => resolve(false),
        style: 'secondary'
      },
      {
        text: 'Confirm',
        onclick: () => resolve(true),
        style: 'primary'
      }
    ];

    showModal(title, message, buttons, true).then(() => {
      // If modal was closed without clicking a button, resolve to false
      if (resolve) {
        resolve(false);
      }
    }).catch(() => {
      resolve(false);
    });
  });
}

// ============================================================================
// LOADING INDICATOR
// ============================================================================

let loadingOverlay = null;

/**
 * Show a loading indicator overlay
 * @param {string} message - Loading message (default: 'Carregando...')
 */
function showLoading(message = 'Carregando...') {
  if (loadingOverlay) {
    hideLoading();
  }

  loadingOverlay = document.createElement('div');
  loadingOverlay.className = 'loading-overlay';
  loadingOverlay.style.position = 'fixed';
  loadingOverlay.style.top = '0';
  loadingOverlay.style.left = '0';
  loadingOverlay.style.width = '100%';
  loadingOverlay.style.height = '100%';
  loadingOverlay.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
  loadingOverlay.style.display = 'flex';
  loadingOverlay.style.justifyContent = 'center';
  loadingOverlay.style.alignItems = 'center';
  loadingOverlay.style.zIndex = '9998';

  const spinner = document.createElement('div');
  spinner.className = 'spinner';
  spinner.innerHTML = `
    <div class="spinner-container">
      <div class="spinner-circle"></div>
      <p>${message}</p>
    </div>
  `;
  spinner.style.textAlign = 'center';
  spinner.style.color = 'white';

  loadingOverlay.appendChild(spinner);
  document.body.appendChild(loadingOverlay);
}

/**
 * Hide the loading indicator
 */
function hideLoading() {
  if (loadingOverlay) {
    loadingOverlay.remove();
    loadingOverlay = null;
  }
}

// ============================================================================
// DATE & TIME FORMATTERS
// ============================================================================

/**
 * Format date to Brazilian format (DD/MM/YYYY)
 * @param {Date|string} date - Date object or string
 * @returns {string} Formatted date
 */
function formatData(date) {
  if (typeof date === 'string') {
    date = new Date(date);
  }
  
  if (!(date instanceof Date) || isNaN(date)) {
    return '';
  }

  const day = String(date.getDate()).padStart(2, '0');
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const year = date.getFullYear();

  return `${day}/${month}/${year}`;
}

/**
 * Format time to HH:MM format
 * @param {string|Date} time - Time string or Date object
 * @returns {string} Formatted time
 */
function formatHora(time) {
  let date;

  if (typeof time === 'string') {
    // Handle HH:MM or HH:MM:SS format
    if (time.includes(':')) {
      return time.substring(0, 5);
    }
    date = new Date(time);
  } else if (time instanceof Date) {
    date = time;
  } else {
    return '';
  }

  if (isNaN(date)) {
    return '';
  }

  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');

  return `${hours}:${minutes}`;
}

// ============================================================================
// CURRENCY & PHONE FORMATTERS
// ============================================================================

/**
 * Format value to Brazilian currency (R$ 1.234,56)
 * @param {number} valor - Value to format
 * @returns {string} Formatted currency string
 */
function formatMoeda(valor) {
  if (typeof valor !== 'number' || isNaN(valor)) {
    return 'R$ 0,00';
  }

  return valor.toLocaleString('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
}

/**
 * Format phone number to (11) 98765-4321 format
 * @param {string} tel - Phone number (digits only)
 * @returns {string} Formatted phone number
 */
function formatTelefone(tel) {
  if (!tel) return '';

  // Remove non-digits
  const digits = tel.replace(/\D/g, '');

  // Format based on length
  if (digits.length === 10) {
    // (XX) XXXX-XXXX
    return `(${digits.substring(0, 2)}) ${digits.substring(2, 6)}-${digits.substring(6)}`;
  } else if (digits.length === 11) {
    // (XX) XXXXX-XXXX
    return `(${digits.substring(0, 2)}) ${digits.substring(2, 7)}-${digits.substring(7)}`;
  } else if (digits.length > 0) {
    // Partial formatting
    return digits;
  }

  return '';
}

// ============================================================================
// TEXT FORMATTERS
// ============================================================================

/**
 * Truncate text to specified length and add ellipsis
 * @param {string} text - Text to truncate
 * @param {number} length - Maximum length
 * @returns {string} Truncated text with ellipsis
 */
function truncateText(text, length) {
  if (!text || typeof text !== 'string') {
    return '';
  }

  if (text.length <= length) {
    return text;
  }

  return `${text.substring(0, length)}...`;
}

/**
 * Format CPF to XXX.XXX.XXX-XX format
 * @param {string} cpf - CPF (digits only)
 * @returns {string} Formatted CPF
 */
function formatCPF(cpf) {
  if (!cpf) return '';

  const digits = cpf.replace(/\D/g, '');

  if (digits.length === 11) {
    return `${digits.substring(0, 3)}.${digits.substring(3, 6)}.${digits.substring(6, 9)}-${digits.substring(9)}`;
  }

  return digits;
}

/**
 * Format CNPJ to XX.XXX.XXX/XXXX-XX format
 * @param {string} cnpj - CNPJ (digits only)
 * @returns {string} Formatted CNPJ
 */
function formatCNPJ(cnpj) {
  if (!cnpj) return '';

  const digits = cnpj.replace(/\D/g, '');

  if (digits.length === 14) {
    return `${digits.substring(0, 2)}.${digits.substring(2, 5)}.${digits.substring(5, 8)}/${digits.substring(8, 12)}-${digits.substring(12)}`;
  }

  return digits;
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Debounce function to limit function calls
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Debounced function
 */
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

/**
 * Copy text to clipboard
 * @param {string} text - Text to copy
 * @returns {Promise<boolean>} Success indicator
 */
function copyToClipboard(text) {
  return navigator.clipboard.writeText(text)
    .then(() => {
      showToast('Copiado para a área de transferência!', 'success');
      return true;
    })
    .catch(() => {
      showToast('Erro ao copiar para a área de transferência', 'error');
      return false;
    });
}

/**
 * Get URL parameter value
 * @param {string} param - Parameter name
 * @returns {string|null} Parameter value or null
 */
function getURLParameter(param) {
  const params = new URLSearchParams(window.location.search);
  return params.get(param);
}

/**
 * Clear all form fields
 * @param {HTMLFormElement} form - Form element
 */
function clearForm(form) {
  if (form && form.reset) {
    form.reset();
  }
}

/**
 * Disable form inputs
 * @param {HTMLFormElement} form - Form element
 * @param {boolean} disabled - Disabled state
 */
function setFormDisabled(form, disabled = true) {
  if (form) {
    const inputs = form.querySelectorAll('input, select, textarea, button');
    inputs.forEach((input) => {
      input.disabled = disabled;
    });
  }
}
