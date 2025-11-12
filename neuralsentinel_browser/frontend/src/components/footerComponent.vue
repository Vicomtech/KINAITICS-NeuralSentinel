<template>
  <div class="footer">
    <a id="about" href="https://www.vicomtech.org/es/" target="_blank" rel="noopener noreferrer">{{ new
      Date().getFullYear() }} &copy; Vicomtech
    </a>
  </div>
</template>

<style>
.footer {
  background-color: white;
  position: fixed;
  bottom: 0px;
  right: 0px;
  display: flex;
  flex-direction: row-reverse;
  justify-content: space-between;
  align-content: flex-end;
  align-items: flex-end;
  width: 100%;
  height: 2rem;
  padding-inline: 2rem;
}
</style>