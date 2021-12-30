<template>
  <div>
    <list-view v-if="this.type === 'directory'" :location="location" />
    <notebook-view v-else-if="this.type === 'notebook'" :location="location" />
    <file-view v-else-if="this.type === 'file'" :location="location" />
    <div v-else class="d-flex justify-content-center">
      <div class="spinner-border" role="status">
        <span class="sr-only">Loading...</span>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import ListView from "./ListView.vue";
import NotebookView from "./NotebookView.vue";
import FileView from "./FileView.vue";

export default {
  name: "ViewChooser",
  components: { ListView, NotebookView, FileView },
  data() {
    return { type: null, location: null };
  },
  created() {
    this.location = window.location.pathname;
    if (this.location === "/") {
      this.location = "/<root>";
    }
    axios.get("/api/info" + this.location).then((response) => {
      this.type = response.data.type;
    });
  },
};
</script>
