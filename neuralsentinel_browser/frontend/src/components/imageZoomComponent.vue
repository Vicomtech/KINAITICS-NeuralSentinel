<template>
  <div v-show="visible" id="zoomcontainer">
    <div id="closebutton" @click="$emit('close')">&Cross;</div>
    <img :src="src" alt="" style="pointer-events: none; width: fit-content; height: fit-content;">
  </div>
</template>

<script setup>

defineProps({
  visible: {
    type: Boolean,
    required: true
  },
  src: {
    type: String,
    required: true
  },
})

</script>

<style>
#closebutton{
  position: fixed;
  border-radius: 50%;
  background-color: rgb(196, 34, 34);
  color:white;
  width: 20px;
  height: 20px;
  right: 20%;
  top:16%;
  cursor: pointer;
}
#zoomcontainer{
  position: fixed;
  width: 60%;
  height: fit-content;
  top:15%;
  left:20%;
  padding: 5px;
  border-radius: 10px;
  box-shadow: 10px 10px 20px rgb(145, 146, 146);
  background-color: white;
  overflow: auto;
}
</style>