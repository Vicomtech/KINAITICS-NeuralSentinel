<template>
  <header-component></header-component>
  <warning-component :visible="warnvisible" :message="warnmessage" :msgtype="wntype"
    @closewarning="warnvisible = false"></warning-component>
  <div id="fullpage">
    <div id="adversarialpage">
      <h4>Adversarial Samples</h4>
      <div class="theader">
        <span>#</span>
        <span>Original</span>
        <span>&Tab;</span>
        <span>Noise</span>
        <span>&Tab;</span>
        <span>Adversarial</span>
      </div>
      <div class="tbody">
        <image-row-component v-for="index in nsamples" :key="index" :index="index"
          :original-image="index <= advurldicts['original'].length ? advurldicts['original'][index - 1] : '/Placeholder_view_vector.png'"
          :noise-image="index <= advurldicts['noise'].length ? advurldicts['noise'][index - 1] : '/Placeholder_view_vector.png'"
          :adversarial-image="index <= advurldicts['adversarial'].length ? advurldicts['adversarial'][index - 1] : '/Placeholder_view_vector.png'"
          @imclicked="(image) => { zoomopen = true; clickedImage = image }"></image-row-component>
      </div>
    </div>
    <div id="resultpage">
      <environment-selection-component id="env-selector"
        @env-changed="(val) => env = val"></environment-selection-component>
      <model-selection-component id="model-selector" @model-changed="(val) => model = val"></model-selection-component>
      <attack-selector-component @sampleschanged="(spl) => { nsamples = spl; }"
        @senddata="(attack, samples, steps) => constructResult(attack, samples, steps)" @attackchanged="(value) => {
          trojantable = value.toLowerCase() == 'trojan'
          original_ac = null
          adversarial_ac = null
          difference_ac = null
          similarity_av = null
          similarity_ma = null
          similarity_mi = null
          original_ac_c0 = null
          original_ac_c1 = null
          difference_ac_c0 = null
          difference_ac_c1 = null
          adversarial_ac_c0 = null
          adversarial_ac_c1 = null
        }"></attack-selector-component>
      <result-table-component v-show="!trojantable" :original_acc="original_ac" :adversarial_acc="adversarial_ac"
        :difference_acc="difference_ac" :similarity_avg="similarity_av" :similarity_max="similarity_ma"
        :similarity_min="similarity_mi"></result-table-component>
      <trojan-table-component v-show="trojantable" :original_acc="original_ac" :adversarial_acc="adversarial_ac"
        :difference_acc="difference_ac" :adversarial_acc_c0="adversarial_ac_c0" :adversarial_acc_c1="adversarial_ac_c1"
        :difference_acc_c0="difference_ac_c0" :difference_acc_c1="difference_ac_c1" :original_acc_c0="original_ac_c0"
        v-bind:original_acc_c1="original_ac_c1"></trojan-table-component>
      <div class="theader" style="width: 50vw; border-inline-width: 2px;">
        <span>Impact</span>
      </div>
      <div id="resimagecontainer" class="tbody">
        <figure v-for="index in nsamples" :key="index">
          <img class="resimage" :src="index <= urlArray.length ? urlArray[index - 1] : '/Placeholder_view_vector.png'"
            @click="(event) => { clickedImage = event.target.src; zoomopen = true }">
          <figcaption>Impact of sample {{ index }}</figcaption>
        </figure>
      </div>
    </div>
  </div>
  <footer-component></footer-component>
  <image-zoom-component @close="zoomopen = false" :visible="zoomopen" :src="clickedImage"></image-zoom-component>
</template>

<script setup>
import { reactive, ref, watch } from "vue";
import { warntype } from "@/modules/utils";

import ImageRowComponent from '@/components/imageRowComponent.vue';
import HeaderComponent from '@/components/headerComponent.vue';
import FooterComponent from '@/components/footerComponent.vue';
import EnvironmentSelectionComponent from "@/components/environmentSelectionComponent.vue";
import modelSelectionComponent from "@/components/modelSelectionComponent.vue";
import ImageZoomComponent from "@/components/imageZoomComponent.vue";
import AttackSelectorComponent from "@/components/attackSelectorComponent.vue";
import ResultTableComponent from "@/components/resultTableComponent.vue";
import TrojanTableComponent from "@/components/trojanTableComponent.vue";
import WarningComponent from "@/components/warningComponent.vue";
import api from "@/modules/updatedapiservice";

import { storeToRefs } from 'pinia'
import { useImageStore } from "@/modules/store/imagestore";

const store = useImageStore()
const { impacsamples, adversarialsamples, adversarialsamplesnumber, impactsamplesnumber } = storeToRefs(store)

const env = ref("")
const model = ref("")

const nsamples = ref(25)
const zoomopen = ref(false)
const clickedImage = ref('Placeholder_view_vector.png')

const warnvisible = ref(false)
const warnmessage = ref("")
const wntype = ref(warntype.INFO)

const original_ac = ref(null)
const adversarial_ac = ref(null)
const difference_ac = ref(null)
const similarity_av = ref(null)
const similarity_ma = ref(null)
const similarity_mi = ref(null)
const original_ac_c0 = ref(null)
const original_ac_c1 = ref(null)
const adversarial_ac_c0 = ref(null)
const adversarial_ac_c1 = ref(null)
const difference_ac_c0 = ref(null)
const difference_ac_c1 = ref(null)
const urlArray = ref(reactive([]))
const advurldicts = reactive({ original: reactive([]), noise: reactive([]), adversarial: reactive([]) })

const trojantable = ref(false)

watch(env, (val, oldval) => {
  if (val != oldval && val != "" && model.value != "") {
    changeEnv()
  }
})

watch(model, (val, oldval) => {
  if (val != oldval && val != "" && env.value != "") {
    changeEnv()
  }
})

watch(impactsamplesnumber, (value, oldvalue) => {
  if (value > oldvalue) {
    urlArray.value.push(URL.createObjectURL(impacsamples.value[oldvalue]))
  }
  else {
    urlArray.value = []
  }
})

watch(adversarialsamplesnumber, (value, oldvalue) => {
  if (value > oldvalue) {

    advurldicts["original"].push(URL.createObjectURL(adversarialsamples.value[oldvalue][0]))
    advurldicts["noise"].push(URL.createObjectURL(adversarialsamples.value[oldvalue][2]))
    advurldicts["adversarial"].push(URL.createObjectURL(adversarialsamples.value[oldvalue][1]))
  }
  else {
    advurldicts.original = reactive([])
    advurldicts.noise = reactive([])
    advurldicts.adversarial = reactive([])
  }
})

function changeEnv() {
  document.getElementById
  warnmessage.value = `Setting ${env.value} environment and ${model.value} scenario. This might take a moment`
  wntype.value = warntype.WARN
  warnvisible.value = true
  api.initializescenario(env.value, model.value).then((value) => {
    if (value == 0) {
      warnmessage.value = `Environment ${env.value} and ${model.value} scenario successfully set.`
      wntype.value = warntype.INFO
    }
    else {
      warnmessage.value = `Error in setting environment ${env.value} and ${model.value} scenario.`
      wntype.value = warntype.ERROR
    }
  })
}

function constructResult(attack, samples, steps) {
  warnmessage.value = `Setting results for ${attack}, ${samples} samples. This might take a moment`
  wntype.value = warntype.WARN
  warnvisible.value = true
  switch (attack.toLowerCase()) {
    case "fgsm":
      api.fgsm(samples).then((result) => {
        original_ac.value = result["original_accuracy"]
        adversarial_ac.value = result["adversarial_accuracy"]
        difference_ac.value = result["difference_accuracy"]
        similarity_av.value = result["avg_similarity"]
        similarity_ma.value = result["max_similarity"]
        similarity_mi.value = result["min_similarity"]
        original_ac_c0.value = null
        original_ac_c1.value = null
        difference_ac_c0.value = null
        difference_ac_c1.value = null
        adversarial_ac_c0.value = null
        adversarial_ac_c1.value = null
        warnvisible.value = false
      })
      break;
    case "bim":
      api.bim(samples, steps).then((result) => {
        original_ac.value = result["original_accuracy"]
        adversarial_ac.value = result["adversarial_accuracy"]
        difference_ac.value = result["difference_accuracy"]
        similarity_av.value = result["avg_similarity"]
        similarity_ma.value = result["max_similarity"]
        similarity_mi.value = result["min_similarity"]
        original_ac_c0.value = null
        original_ac_c1.value = null
        difference_ac_c0.value = null
        difference_ac_c1.value = null
        adversarial_ac_c0.value = null
        adversarial_ac_c1.value = null
        warnvisible.value = false
      })
      break;
    case "pgd":
      api.pgd(samples, steps).then((result) => {
        original_ac.value = result["original_accuracy"]
        adversarial_ac.value = result["adversarial_accuracy"]
        difference_ac.value = result["difference_accuracy"]
        similarity_av.value = result["avg_similarity"]
        similarity_ma.value = result["max_similarity"]
        similarity_mi.value = result["min_similarity"]
        original_ac_c0.value = null
        original_ac_c1.value = null
        difference_ac_c0.value = null
        difference_ac_c1.value = null
        adversarial_ac_c0.value = null
        adversarial_ac_c1.value = null
        warnvisible.value = false
      })
      break;
    case "trojan":
      api.trojan(samples, steps).then((result) => {
        if (result.status == 200) {
          console.log(result)
          original_ac.value = result.data["original_accuracy"]
          adversarial_ac.value = result.data["adversarial_accuracy"]
          difference_ac.value = result.data["difference_accuracy"]
          similarity_av.value = null
          similarity_ma.value = null
          similarity_mi.value = null
          original_ac_c0.value = result.data["original_accuracy_by_classes"][0]
          original_ac_c1.value = result.data["original_accuracy_by_classes"][1]
          difference_ac_c0.value = result.data["difference_accuracy_by_classes"][0]
          difference_ac_c1.value = result.data["difference_accuracy_by_classes"][1]
          adversarial_ac_c0.value = result.data["adversarial_accuracy_by_classes"][0]
          adversarial_ac_c1.value = result.data["adversarial_accuracy_by_classes"][1]
          warnvisible.value = false
        } else {
          warnmessage.value = result.data
          wntype.value = warntype.ERROR
        }
      })
      break;
    default:
      wntype.value = warntype.ERROR
      warnmessage.value = `error getting results`
      warnvisible.value = true
      break;
  }

}
</script>

<style>
#adversarialpage {
  width: auto;
  min-width: 35%;
  padding: 1vw;
  justify-content: center;
  flex-grow: 1;
}

#fullpage {
  display: flex;
  flex-direction: row;
  width: 98%;
  height: 78%;
  flex-wrap: wrap;
  margin-bottom: 3rem;
  padding-inline: 1vw;
}

#resimagecontainer {
  display: flex;
  flex-direction: row;
  justify-content: center;
  flex-wrap: wrap;
  border: 2px solid rgb(3, 37, 100);
  min-height: 120px;
  max-height: 40vh;
  width: 50vw;
  margin-bottom: 3rem;
}

#resultpage {
  display: flex;
  flex-direction: column;
  justify-items: center;
  align-content: center;
  align-items: center;
  width: auto;
  min-width: 350px;
  padding: 1vw;
  flex-wrap: wrap;
}

.resimage {
  width: auto;
  height: 100px;
  margin-inline: 0.5vw;
  margin-block: 0.5vh;
  aspect-ratio: auto;
  cursor: zoom-in;
}

.tbody {
  border-inline: 1px solid rgb(3, 37, 100);
  height: fit-content;
  max-height: 65vh;
  overflow-y: auto;
}

.theader {
  display: flex;
  flex-direction: row;
  justify-content: space-around;
  height: auto;
  padding-block: 5px;
  align-items: center;
  background-color: rgb(3, 37, 100);
  border-inline: 1px solid rgb(3, 37, 100);
  color: white;
  border-bottom: 4px solid rgb(3, 37, 100);
  margin-top: 0px;
}

figure {
  display: flex;
  flex-direction: column;
  width: auto;
  height: 120px;
  border: double 4px rgb(3, 37, 100);
  margin: 1%;
  padding: 1%;
}

figcaption {
  margin-top: 0.2%;
  font-family: Garamond, serif;
  font-style: normal;
  font-weight: bold;
  font-size: 0.8rem;
}
</style>