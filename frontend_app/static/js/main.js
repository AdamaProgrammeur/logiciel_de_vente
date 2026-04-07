// === Sidebar toggle ===
document.addEventListener('DOMContentLoaded', function () {
    const sidebarToggleBtn = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar-wrapper');

    sidebarToggleBtn.addEventListener('click', function () {
        sidebar.classList.toggle('d-none');
    });
});

// === Formatage utils ===
function formatCurrency(value) {
    return parseFloat(value).toLocaleString('fr-FR', { style: 'currency', currency: 'XOF' });
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('fr-FR');
}

// === Modal helpers (optionnel) ===
function hideModal(modalId) {
    const modalEl = document.getElementById(modalId);
    const modal = bootstrap.Modal.getInstance(modalEl);
    if (modal) modal.hide();
}

function showModal(modalId) {
    const modalEl = document.getElementById(modalId);
    const modal = new bootstrap.Modal(modalEl);
    modal.show();
}

// === Auto-initialize Bootstrap tooltips if needed ===
document.addEventListener('DOMContentLoaded', function () {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});