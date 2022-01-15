<template>
  <div class="row">
    <error-view v-if="error" :error="error" />
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
          :href="'/api/raw' + location + '?download=1'"
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
import ErrorView from "./ErrorView.vue";

export default {
  name: "NotebookView",
  props: ["location", "private"],
  components: { Toc, ErrorView },
  data() {
    return { html: null, toc: null, importURL: null, error: null };
  },
  created() {
    this.loader = this.$loading.show({ canCanel: false });
    var importAPI = this.private
      ? "/api/notebook/private-import"
      : "/api/notebook/import";
    axios.get(importAPI + this.location).then((response) => {
      this.importURL = response.data;
    });

    var tocAPI = this.private
      ? "/api/notebook/private-toc"
      : "/api/notebook/toc";
    axios
      .get(tocAPI + this.location)
      .then((response) => {
        this.toc = response.data;
      })
      .catch((error) => {
        this.error = error;
      });

    var renderAPI = this.private
      ? "/api/notebook/private-render"
      : "/api/notebook/render";
    axios
      .get(renderAPI + this.location)
      .then((response) => {
        this.html = response.data;
      })
      .catch((error) => {
        this.error = error;
        this.loader.hide();
      });
  },
  methods: {
    goToAnchor(anchor) {
      var elem =
        this.$refs.notebook.contentWindow.document.getElementById(anchor);
      this.$refs.notebook.contentWindow.scrollTo({ top: elem.offsetTop });
    },
    load() {
      if (this.html) {
        this.loader.hide();
      }
      var hash = window.location.hash;
      if (hash) {
        this.goToAnchor(hash.slice(1));
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
