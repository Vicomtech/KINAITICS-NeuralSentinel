<template>
  <div id="optioncontainer">
    <div class="row selectdiv">
      <label for="models">Choose a scenario:</label>
      <select name="models" id="models" v-model="model" onfocus="this.size=2;" onblur="this.size=0;"
        onchange="this.size=1; this.blur();">
        <option v-for="elem in options" :value="elem">{{ elem }}</option>
      </select>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from "vue";
const model = ref("");
const options = ref(["Original", "Adversarial Training", "Dimensionality Reduction", "Prediction Similarity"])

const emit = defineEmits(['modelChanged'])

watch(model, async (newmod) => {
  emit('modelChanged', newmod)
})

onMounted(() => {
  model.value = "Original"
})

</script>

<style>
#models {
  width: fit-content;
}

.selectdiv {
  width: 100%;
}

.selectdiv select {
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
  /* Add some styling */

  display: block;
  height: 100%;
  margin: 5px 0px;
  padding: 0px 24px;
  font-size: 1rem;
  color: rgb(3, 37, 100);
  background-color: #ffffff;
  background-image: none;
  border: 1px solid rgb(3, 37, 100);
  -ms-word-break: normal;
  word-break: normal;
}

select option:hover {
  box-shadow: 0 0 10px 100px rgb(3, 37, 100) inset !important;
  color: white !important;
  cursor: pointer;
}

select option:checked {
  box-shadow: 0 0 10px 100px rgb(212, 212, 212) inset !important;
  color: rgb(3, 37, 100) !important;
  cursor: default;
}
</style>