<template>
  <table>
    <thead>
      <tr>
        <th colspan="2">Accuracy</th>
        <th colspan="2">Accuracy by Class</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <th>Original Accuracy</th>
        <td>{{ original_acc ? original_acc : "" }}</td>
        <td>
          <p><b>Class 0:</b> {{ original_acc_c0 ? original_acc_c0 : "" }}</p>
        </td>
        <td>
          <p><b>Class 1:</b> {{ original_acc_c1 ? original_acc_c1 : "" }}</p>
        </td>
      </tr>
      <tr>
        <th>Adversarial Accuracy</th>
        <td>{{ adversarial_acc ? adversarial_acc : "" }}</td>
        <td>
          <p><b>Class 0:</b> {{ adversarial_acc_c0 ? adversarial_acc_c0 : "" }}</p>
        </td>
        <td>
          <p><b>Class 1:</b> {{ adversarial_acc_c1 ? adversarial_acc_c1 : "" }}</p>
        </td>
      </tr>
      <tr>
        <th>Difference Accuracy</th>
        <td>{{ difference_acc ? difference_acc : "" }}</td>
        <td>
          <p><b>Class 0:</b> {{ difference_acc_c0 ? difference_acc_c0 : "" }}</p>
        </td>
        <td>
          <p><b>Class 1:</b> {{ difference_acc_c1 ? difference_acc_c1 : "" }}</p>
        </td>
      </tr>
    </tbody>
  </table>
</template>

<script setup>

defineProps({
  original_acc: {
    type: Number,
    required: false
  },
  adversarial_acc: {
    type: Number,
    required: false
  },
  difference_acc: {
    type: Number,
    required: false
  },
  original_acc_c0: {
    type: Number,
    required: false
  },
  adversarial_acc_c0: {
    type: Number,
    required: false
  },
  difference_acc_c0: {
    type: Number,
    required: false
  },
  original_acc_c1: {
    type: Number,
    required: false
  },
  adversarial_acc_c1: {
    type: Number,
    required: false
  },
  difference_acc_c1: {
    type: Number,
    required: false
  },
})
</script>

<style></style>