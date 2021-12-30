<template>
  <iframe id="file-viewer" :src="'/api/raw' + location" />
</template>


<script>
export default {
  name: "FileView",
  props: ["location"],
};
</script>

<style scoped>
#file-viewer {
  width: 100%;
  height: 95vh;
}
</style>
