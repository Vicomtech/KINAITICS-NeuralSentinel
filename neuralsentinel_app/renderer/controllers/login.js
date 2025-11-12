window.addEventListener('DOMContentLoaded', () => {
  document.getElementById('current-year').textContent = new Date().getFullYear();

  const form = document.getElementById('loginForm');
  const errorMsg = document.getElementById('errorMsg');

  form.addEventListener('submit', async e => {
    e.preventDefault();
    const user = document.getElementById('username').value.trim();
    const pass = document.getElementById('password').value.trim();

    // (DEBUG) Show entered credentials
    //alert(`Username: ${user}\nPassword: ${pass}`);

    // Validate against database
    const valid = await window.electronAPI.validateUser(user, pass);

    if (valid) {
      window.electronAPI.log(`User "${user}" logged in.`);
      window.electronAPI.startAuthenticator(user);
      errorMsg.textContent = '';
      window.location.href = 'index.html';
    } else {
      errorMsg.textContent = 'Invalid credentials';
    }
  });
});