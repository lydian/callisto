<template>
  <nav aria-label="breadcrumb">
    <ol class="breadcrumb">
      <li class="breadcrumb-item" aria-current="page">
        <a href="/">&lt;root&gt;</a>
      </li>
      <li
        v-for="(item, index) in components.slice(0, -1)"
        :key="item"
        class="breadcrumb-item"
        aria-current="page"
      >
        <a
          v-bind:href="
            '/' +
            components
              .slice(0, index + 1)
              .map((x) => encodeURIComponent(x))
              .join('/')
          "
          >{{ item }}
        </a>
      </li>
      <li class="breadcrumb-item" aria-current="page">
        {{ components[components.length - 1] }}
      </li>
    </ol>
  </nav>
</template>

<script>
export default {
  name: "Breadcrump",
  data() {
    return {
      components: window.location.pathname
        .split("/")
        .slice(1)
        .map((x) => decodeURIComponent(x)),
    };
  },
};
</script>
