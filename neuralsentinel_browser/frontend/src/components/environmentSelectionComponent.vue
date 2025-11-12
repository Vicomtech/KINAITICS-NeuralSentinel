<template>
  <div id="optioncontainer">
    <div class="row selectdiv">
      <label for="environments">Choose an Environment:</label>
      <select name="environments" id="environments" v-model="env" onfocus="this.size=2;" onblur="this.size=0;"
        onchange="this.size=1; this.blur();">
        <option v-for="elem in options" :value="elem">{{ elem }}</option>
      </select>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from "vue";
const env = ref("");
const options = ref(["Breast Cancer", "Brain Cancer", "Aortic Calcification"])

const emit = defineEmits(['envChanged'])

watch(env, async (newenv) => {
  emit('envChanged', newenv)
})

onMounted(() => {
  env.value = "Breast Cancer"
})

</script>

<style>
#environments {
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