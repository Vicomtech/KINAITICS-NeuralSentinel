window.addEventListener('DOMContentLoaded', () => {
  // Update the current year dynamically in the footer
  document.getElementById('current-year').textContent = new Date().getFullYear();
  
  // Wiring for the buttons
  document.getElementById('btnUpload').addEventListener('click', () => {
    window.location.href = 'upload.html'; // Navigate to upload page
  });
  document.getElementById('btnDashboard').addEventListener('click', () => {
    window.location.href = 'dashboard.html'; // Navigate to dashboard page
  });
});