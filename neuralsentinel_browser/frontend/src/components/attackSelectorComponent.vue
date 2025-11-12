<template>
  <div id="attackselectioncontainer">
    <div id="attackgroup">
      <input type="radio" id="fgsm" name="att_group" value="fgsm" checked="true"
        @input="(event) => selectedAttack = event.target.value" />
      <label for=" fgsm">FGSM</label><br />
      <input type="radio" id="pgd" name="att_group" value="pgd"
        @input="(event) => selectedAttack = event.target.value" />
      <label for="pgd">PGD</label><br />
      <input type="radio" id="bin" name="att_group" value="bim"
        @input="(event) => selectedAttack = event.target.value" />
      <label for="bin">BIM</label>
      <input type="radio" id="trojan" name="att_group" value="trojan"
        @input="(event) => selectedAttack = event.target.value" />
      <label for="trojan">TROJAN</label>
    </div>
    <div id="paramgroup">
      <label for="samples"> Sample number:</label>
      <input id="samples" type="number" v-model="samples" min="1" />
      <label for="step"> Step:</label>
      <input id="step" type="number" v-model="steps" min="1" :disabled="selectedAttack == 'fgsm'" />
    </div>
  </div>
  <div id="butrow" class="row">
    <button class="button"
      @click="() => { resetstore(); $emit('senddata', selectedAttack, samples, steps) }">SEND</button>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from "vue";
import { useImageStore } from "@/modules/store/imagestore";

const store = useImageStore()
const { resetstore } = store
const samples = ref(1)
const steps = ref(1)
const selectedAttack = ref("fgsm")

const emit = defineEmits(['sampleschanged', 'senddata', 'attackchanged'])

onMounted(() => {
  emit("sampleschanged", samples.value)
})

watch(selectedAttack, (value, oldvalue) => {
  if (value != oldvalue) {
    emit("attackchanged", value)
  }
})

watch(samples, (value) => {
  emit("sampleschanged", value)
})

</script>

<style>
#attackgroup,
#paramgroup {
  display: flex;
  direction: column;
  align-content: center;
  justify-items: center;
  justify-content: center;
  align-items: center;
  height: fit-content;
}

#attackselectioncontainer {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  width: 90%;
  justify-content: space-around;
}

#butrow {
  display: flex;
  flex-direction: row;
  justify-content: flex-end;
  width: 90%;
}
</style>