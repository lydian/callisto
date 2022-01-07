<template>
  <div v-if="error">
    <div class="alert alert-danger">
      <strong>{{ error.code }} {{ error.name }}</strong>
      {{ error.message }}
    </div>
  </div>
</template>

<script>
export default {
  name: "ErrorView",
  props: ["error"],
};
</script>
