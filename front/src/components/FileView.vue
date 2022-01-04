<template>
  <div>
    <error-view v-if="this.error" :error="error" />

    <iframe
      v-else
      id="file-viewer"
      ref="fileViewer"
      :src="'/api/raw' + location"
      @load="checkError"
    />
  </div>
</template>


<script>
import ErrorView from "./ErrorView.vue";

export default {
  name: "FileView",
  props: ["location"],
  components: { ErrorView },
  data() {
    return { error: null };
  },
  methods: {
    checkError() {
      try {
        var pre =
          this.$refs.fileViewer.contentDocument.getElementsByTagName("pre")[0];
        var output = JSON.parse(pre.innerHTML);
        if (output.code == 404) {
          this.error = output;
        }
      } catch {
        // no errors found
      }
    },
  },
};
</script>

<style scoped>
#file-viewer {
  width: 100%;
  height: 95vh;
}
</style>
