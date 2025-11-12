<template>
  <table>
    <thead>
      <tr>
        <th colspan="2">Accuracy</th>
        <th colspan="2">Similarity</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <th>Original Accuracy</th>
        <td>{{ original_acc ? original_acc : "" }}</td>
        <th>AVG Similarity</th>
        <td>{{ similarity_avg ? similarity_avg : "" }}</td>
      </tr>
      <tr>
        <th>Adversarial Accuracy</th>
        <td>{{ adversarial_acc ? adversarial_acc : "" }}</td>
        <th>MAX Similarity</th>
        <td>{{ similarity_max ? similarity_max : "" }}</td>
      </tr>
      <tr>
        <th>Difference Accuracy</th>
        <td>{{ difference_acc ? difference_acc : "" }}</td>
        <th>MIN Similarity</th>
        <td>{{ similarity_min ? similarity_min : "" }}</td>
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
  similarity_avg: {
    type: Number,
    required: false
  },
  similarity_max: {
    type: Number,
    required: false
  },
  similarity_min: {
    type: Number,
    required: false
  },
})
</script>

<style></style>