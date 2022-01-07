<template>
  <div>
    <div class="container">
      <breadcrump v-if="!this.privateLink"></breadcrump>
    </div>
    <error-view v-if="this.error" :error="error" />
    <list-view v-else-if="this.type === 'directory'" :location="location" />
    <notebook-view
      v-else-if="this.type === 'notebook'"
      :location="location"
      :private="privateLink"
    />
    <file-view v-else-if="this.type === 'file'" :location="location" />
  </div>
</template>

<script>
import axios from "axios";
import ListView from "./ListView.vue";
import NotebookView from "./NotebookView.vue";
import FileView from "./FileView.vue";
import ErrorView from "./ErrorView.vue";
import Breadcrump from "./Breadcrump.vue";

export default {
  name: "ViewChooser",
  components: { ListView, NotebookView, FileView, ErrorView, Breadcrump },
  data() {
    return { type: null, location: null, error: null, privateLink: null };
  },
  created() {
    this.location = window.location.pathname;
    if (this.location.startsWith("/private")) {
      this.location = "/" + this.location.substring(9); // remove "/private"
      console.log(this.location);
      this.privateLink = true;
      this.type = "notebook";
      console.log(this.location);
      return;
    }

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
