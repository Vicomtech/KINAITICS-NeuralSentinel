<template>
  <div id="maincontainer">
    <span class="rowsymbol">{{index}}</span>
    <img class="rowdisplay" :src="originalImage" alt="" @click="$emit('imclicked', originalImage)">
    <span class="rowsymbol">&plus;</span>
    <img class="rowdisplay" :src="noiseImage" alt="" @click="$emit('imclicked', noiseImage)">
    <span class=" rowsymbol">&equals;</span>
    <img class="rowdisplay" :src="adversarialImage" alt="" @click="$emit('imclicked', adversarialImage)">
  </div>
</template>

<script setup>
  defineEmits(['imclicked'])
  defineProps({
    index: {
        type: Number,
        default:0
      },
    originalImage: {
      type: String,
      default: 'Placeholder_view_vector.png'
    },
    noiseImage: {
      type: String,
      default: 'Placeholder_view_vector.png'
    },
    adversarialImage: {
      type: String,
      default: 'Placeholder_view_vector.png'
    }
  })
</script>

<style>
#maincontainer {
  display: flex;
  flex-direction: row;
  justify-content: space-around;
  height: auto;
  padding-block: 5px;
  width: 100%;
  align-items: center;
  border-bottom: 1px solid rgb(3, 37, 100);
}

.rowdisplay{
  width: auto;
  height: 60px;
  border: 1px solid black;
  aspect-ratio: auto;
  cursor: zoom-in;
}

.rowsymbol {
  color:rgb(3, 37, 100);
}

</style>