<template>
  <div>
    <div class="d-flex w-100 justify-content-end">
      <input
        ref="keyword"
        v-model="keyword"
        placeholder="filter file name"
        type="text"
      />
    </div>
    <div v-if="this.files === null">
      <div class="spinner-border" role="status">
        <span class="sr-only"></span>
      </div>
    </div>
    <div id="list" class="list-group">
      <a
        v-for="item in matchedFiles"
        :key="item.name"
        v-bind:href="'/' + item.path"
        class="list-group-item list-group-item-action"
        role="tabpanel"
      >
        <div class="d-flex w-100 justify-content-between">
          <span class="mb-1">
            <!-- folder icon -->
            <span v-if="item.type === 'directory'">&#128193;</span>
            <!-- notebook icon -->
            <span v-else-if="item.type === 'notebook'">&#128221;</span>
            <!-- File icon -->
            <span v-else>&#128196;</span>

            <span>&nbsp;&nbsp;{{ item.name }}</span>
          </span>
          <small>{{ readableTime(item.last_modified) }}</small>
        </div>
      </a>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import moment from "moment";

export default {
  name: "ListView",
  props: ["location"],
  data() {
    return { files: null, keyword: "" };
  },
  created() {
    this.fetchList(3);
  },
  mounted() {
    this.$refs.keyword.focus();
  },
  computed: {
    matchedFiles: {
      get: function () {
        if (this.keyword) {
          return this.files.filter((f) =>
            f.name.toLowerCase().includes(this.keyword.toLowerCase())
          );
        }
        return this.files;
      },
    },
  },
  methods: {
    fetchList(reload_seconds) {
      axios
        .get("/api/get" + this.location)
        .then((response) => {
          this.files = response.data.content;
          setTimeout(() => {
            this.fetchList(reload_seconds);
          }, reload_seconds * 1000);
        })
        .catch((error) => {
          console.log(error.toJSON());

          setTimeout(() => {
            this.fetchList(reload_seconds * 2);
          }, reload_seconds * 2 * 1000);
        });
    },
    readableTime(timeString) {
      return moment(timeString).calendar(null, { sameElse: "YYYY-MM-DD" });
    },
  },
  beforeDestory() {
    this.cancelUpdate();
  },
};
</script>
