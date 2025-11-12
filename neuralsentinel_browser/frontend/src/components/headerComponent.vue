<template>
  <div class="header">
    <img class="logo" :src="vicom_Url" alt="vicomtech" />
    <h2>Neural Sentinel</h2>
    <img class="logo" :src="kinatiks_Url" alt="Kinaitics" />
  </div>
</template>

<script setup>
  import kinatiks_Url from '/Kinatiks_logo.svg'
  import vicom_Url from '/logo-vicom.png'
</script>

<style>

.header {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  flex-wrap: wrap;
  width: auto;
  height: 6%;
  padding: 1%;
  background-color: #ffffff;
  box-shadow: inset 0px 0px 12px 12px #c2edf5,
    inset 5px 5px 20px 20px rgb(240, 252, 255);
  align-content: center;
  align-items: center;
  border: outset 4px #bff5ff;
}

.logo {
  display: flex;
  max-width: 10%;
}

</style>