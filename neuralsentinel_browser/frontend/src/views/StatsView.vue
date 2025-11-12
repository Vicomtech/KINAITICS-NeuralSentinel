<template>
  <div id="container">
    <figure id="Interpretability">
      <img class="resultim" id="inter_img" :src="interpretability" alt="Interpretability" @error="(event) => {
        event.onerror = null;
        event.target.src = 'Placeholder_view_vector.png';
      }
        " />
      <figcaption id="Interpretability_caption">Interpretability</figcaption>
    </figure>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute()
const interpretability = ref("")

onMounted(() => {
  console.log(route.params.name)
  if (route.params.name.includes("Placeholder")) {
    interpretability.value = `/${route.params.name}`
  } else {
    interpretability.value = `/images/interpretability/${route.params.name}.jpeg`
  }
})

</script>

<style scoped>
#container {
  height: 100%;
  width: 100%;
  display: flex;
  justify-content: center;
}

#Interpretability {
  height: 95%;
  width: auto;
  overflow: hidden;
}

#Interpretability_caption {
  margin-top: 1%;
  font-family: Garamond, serif;
  font-style: italic;
  font-weight: bold;
  font-size: 2rem;
}
</style>