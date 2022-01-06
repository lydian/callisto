<template>
  <div>
    <error-view v-if="this.error" :error="error" />
    <list-view v-else-if="this.type === 'directory'" :location="location" />
    <notebook-view v-else-if="this.type === 'notebook'" :location="location" />
    <file-view v-else-if="this.type === 'file'" :location="location" />
  </div>
</template>

<script>
import axios from "axios";
import ListView from "./ListView.vue";
import NotebookView from "./NotebookView.vue";
import FileView from "./FileView.vue";
import ErrorView from "./ErrorView.vue";

export default {
  name: "ViewChooser",
  components: { ListView, NotebookView, FileView, ErrorView },
  data() {
    return { type: null, location: null, error: null };
  },
  created() {
    this.location = window.location.pathname;
    if (this.location === "/") {
      this.location = "/<root>";
    }
    var loader = this.$loading.show({ canCanel: false });
    axios
      .get("/api/info" + this.location)
      .then((response) => {
        this.type = response.data.type;
        loader.hide();
      })
      .catch((errorInfo) => {
        console.log("here");
        console.log(errorInfo.response.data);
        this.error = {
          code: errorInfo.response.status,
          name: errorInfo.response.data.name,
          message: errorInfo.response.data.description,
        };
      });
  },
};
</script>
