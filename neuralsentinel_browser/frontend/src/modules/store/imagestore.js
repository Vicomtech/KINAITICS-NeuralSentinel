import { defineStore } from 'pinia'

import { ref, computed } from "vue";

import { base64ToBlob } from '../utils';


export const useImageStore = defineStore('image', () => {
  const adversarialsamples = ref([[Blob]])
  const impacsamples = ref([Blob])

  const loadingadversarials = ref(false)
  const loadingimpact = ref(false)
  
  const adversarialsamplesnumber = computed(()=>adversarialsamples.value.length)
  const impactsamplesnumber = computed(()=>impacsamples.value.length)


  /**
   * Resets the store by emptying the image banks
   */
  function resetstore() {
    adversarialsamples.value = []
    impacsamples.value = []
    loadingadversarials.value = false
    loadingimpact.value = false
  }

  /**
   * Decodifies an image in base64 and adds it to the impact samples bank
   * @param {Blob} image
   */
  function addImpactBlob(image) {
    impacsamples.value = impacsamples.value.concat([image])
  }

  /**
   * Decodifies the 3 images of an adversarial sample (original, noise, adversarial) and adds them to adversarial sample bank
   * @param {[String,String,String]} tuple: the tuple of three values containing the images coded in base64
   */
  function addadversarialsamples(tuple) {
    const imtuple = []
    imtuple.push(base64ToBlob(tuple[0], 'image/jpeg'), base64ToBlob(tuple[1], 'image/jpeg'), base64ToBlob(tuple[2], 'image/jpeg'))
    adversarialsamples.value.push(imtuple)
  }

  function switchadversarialloadstatus() {
    loadingadversarials.value = !loadingadversarials.value
  }

  function switchimpactloadstatus() {
    loadingimpact.value = !loadingimpact.value
  }

  return { adversarialsamples, impacsamples, loadingadversarials, loadingimpact, adversarialsamplesnumber, impactsamplesnumber, resetstore, addImpactBlob, addadversarialsamples, switchadversarialloadstatus, switchimpactloadstatus }
})