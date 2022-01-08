<template>
  <div>
    <h5>Table of Contents</h5>
    <hr />
    <ul class="navbar-nav">
      <li v-for="h1 in content" v-bind:key="h1.anchor" class="nav-item">
        <a
          :href="'#' + h1.anchor"
          v-if="h1.text"
          v-on:click="click(h1.anchor)"
          >{{ h1.text }}</a
        >
        <ul v-if="h1.children">
          <li v-for="h2 in h1.children" :key="h2.anchor" class="nav-item">
            <a
              :href="'#' + h2.anchor"
              v-if="h2.text"
              v-on:click="click(h2.anchor)"
              >{{ h2.text }}</a
            >
            <ul v-if="h2.children">
              <li v-for="h3 in h2.children" :key="h3.anchor" class="nav-item">
                <a
                  :href="'#' + h3.anchor"
                  v-if="h3.text"
                  v-on:click="click(h3.anchor)"
                  >{{ h3.text }}</a
                >
                <ul v-if="h3.children">
                  <li
                    v-for="h4 in h3.children"
                    :key="h4.anchor"
                    class="nav-item"
                  >
                    <a
                      :href="'#' + h4.anchor"
                      v-if="h4.text"
                      v-on:click="click(h4.anchor)"
                      >{{ h4.text }}</a
                    >
                    <ul v-if="h4.children">
                      <li
                        v-for="h5 in h4.children"
                        :key="h5.anchor"
                        class="nav-item"
                      >
                        <a
                          :href="'#' + h5.anchor"
                          v-if="h5.text"
                          v-on:click="click(h5.anchor)"
                          >{{ h5.text }}
                        </a>
                      </li>
                    </ul>
                  </li>
                </ul>
              </li>
            </ul>
          </li>
        </ul>
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  name: "Toc",
  props: ["content"],
  methods: {
    click(anchor) {
      this.$emit("clicked", anchor);
    },
  },
};
</script>
