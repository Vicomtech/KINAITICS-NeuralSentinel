<template>
  <div id="msgcontainer" v-if="visible" :class="`${msgtype.toLowerCase()}style`">
    <span>{{ message }}</span> <button id="closemsg" v-if="msgtype != warntype.WARN" @click="$emit('closewarning')">&Cross;</button>
  </div>
</template>

<script setup>

import { warntype } from '@/modules/utils';

defineEmits(['closewarning'])

const props = defineProps({
  message: {
    type: String,
    default:""
  },
  msgtype: {
    type: String,
    validator(value) {
      return Object.keys(warntype).includes(value)
    },
    default: warntype.INFO,
  },
  visible: {
    type: Boolean,
    default: false
  }
})

</script>

<style>
#msgcontainer{
  display: flex;
  justify-content: space-between;
  padding-left: 40%
}

.errorstyle {
  background-color: rgb(220, 40, 40);
  color:white
}

.warnstyle {
  background-color: rgb(220, 140, 40);
  color: white
}

.infostyle {
  background-color: rgb(211, 211, 211);
  color: rgb(3, 37, 100);
}
</style>