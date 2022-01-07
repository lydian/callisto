<template>
  <div class="row">
    <div class="col-3 bg-light side">
      <toc
        style="height: 95vh"
        v-bind:content="this.toc"
        @clicked="goToAnchor"
      />
    </div>
    <div class="col-9">
      <div class="text-end">
        <a
          class="btn btn-outline-primary"
          role="button"
          :href="'/api/raw/' + location + '?download=1'"
          >Download</a
        >
        <a
          class="btn btn-outline-primary"
          v-if="importURL"
          role="button"
          :href="importURL"
          target="_blank"
          >Import</a
        >
      </div>
      <iframe
        style="width: 100%; min-height: 95vh"
        id="notebook"
        ref="notebook"
        :srcdoc="html"
        @load="load"
      ></iframe>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import Toc from "./Toc.vue";

export default {
  name: "NotebookView",
  props: ["location"],
  components: { Toc },
  data() {
    return { html: null, toc: null, importURL: null };
  },
  created() {
    var loader = this.$loading.show({ canCanel: false });
    axios.get("/api/notebook/import" + this.location).then((response) => {
      this.importURL = response.data;
    });

    axios.get("/api/notebook/toc" + this.location).then((response) => {
      this.toc = response.data;
      this.hideLoading(loader);
    });

    axios.get("/api/notebook/render" + this.location).then((response) => {
      this.html = response.data;
      this.hideLoading(loader);
    });
  },
  methods: {
    goToAnchor(anchor) {
      var elem =
        this.$refs.notebook.contentWindow.document.getElementById(anchor);
      this.$refs.notebook.contentWindow.scrollTo({ top: elem.offsetTop });
    },
    load() {
      console.log(window.location.hash);
      var hash = window.location.hash;
      if (hash) {
        this.goToAnchor(hash.slice(1));
      }
    },
    hideLoading(loader) {
      if (this.html && this.toc) {
        loader.hide();
      }
    },
  },
};
</script>

<style scoped>
.side {
  height: 95vh;
  padding-top: 15px;
}
</style>
