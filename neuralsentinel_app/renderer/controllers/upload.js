/**
 * Wrapper function to send log events securely via Electron's API.
 * @param {string} msg - The log message to be sent.
 */
function logEvent(msg) {
  window.electronAPI.log(msg);
}

// Event listener for when the DOM content is fully loaded.
window.addEventListener('DOMContentLoaded', () => {
  //logEvent('upload.js DOMContentLoaded');

  // Get references to the upload buttons
  const uploadDatasetBtn = document.getElementById('uploadDatasetBtn');
  const uploadModelBtn   = document.getElementById('uploadModelBtn');

  // Event listener for the "Upload Dataset" button
  if (uploadDatasetBtn) {
    uploadDatasetBtn.addEventListener('click', () => {
      logEvent('[USER] Upload Dataset button clicked');
      startUpload('datasets', 'dataset');
    });
  }

  // Event listener for the "Upload Model" button
  if (uploadModelBtn) {
    uploadModelBtn.addEventListener('click', () => {
      logEvent('[USER] Upload Model button clicked');
      startUpload('models', 'model');
    });
  }
  
  // Event listener for the "Back to Dashboard" button
  const backBtn = document.getElementById('backToDashboardBtn');
  if (backBtn) {
    backBtn.addEventListener('click', () => {
      window.location.href = 'dashboard.html'; // Navigate back to the dashboard
    });
  }
});

/**
 * Handles the upload flow for datasets or models.
 * @param {string} subfolder - The subfolder where the file will be uploaded ('datasets' or 'models')
 * @param {string} fileType  - The type of file being uploaded ('dataset' or 'model')
 */
async function startUpload(subfolder, fileType) {
  const { uploadAndCalc } = window.electronAPI;

  // 1) Show an “Uploading…” message
  const loadingId = 'upload-loading';
  const loadingText = fileType === 'model'
    ? 'Uploading model…'
    : 'Uploading dataset…';
  const loadingDiv = document.createElement('div');
  loadingDiv.id = loadingId;
  Object.assign(loadingDiv.style, {
    position: 'fixed',
    top: '20px',
    right: '20px',
    padding: '10px 15px',
    background: '#333',
    color: '#fff',
    borderRadius: '4px',
    fontFamily: 'sans-serif',
    zIndex: 9999,
  });
  loadingDiv.textContent = loadingText;
  document.body.appendChild(loadingDiv);

  try {
    // Trigger the upload process
    const result = await uploadAndCalc({ subfolder, fileType });
    if (!result.success) {
      const msg = result.error || 'Unknown upload error';
      alert(`Upload failed: ${msg}`);
      logEvent(`Upload error: ${msg}`);
      return;
    }

    logEvent(`[USER] File uploaded: ${result.fileName}`);
    // Persist the uploaded file info for the next screen
    localStorage.setItem('lastUploadedFile', result.fileName);
    localStorage.setItem('lastUploadedType', result.fileType);

    // Notify the user and redirect
    alert(`File uploaded successfully: ${result.fileName}\nRedirecting to dashboard…`);
    window.location.href = 'dashboard.html'; // Redirect to the dashboard after successful upload

  } catch (err) {
    // Catch any unexpected errors
    console.error('Upload exception:', err);
    alert(`Unexpected error: ${err.message}`);
    logEvent(`Upload exception: ${err.message}`);
  } finally {
    // 3) Remove the “Uploading…” message
    const old = document.getElementById(loadingId);
    if (old) old.remove();
  }
}
