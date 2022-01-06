import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap/dist/js/bootstrap.min.js';
import "vue-loading-overlay/dist/vue-loading.css";
import 'bootstrap-vue/dist/bootstrap-vue.css'

import Vue from 'vue/dist/vue.js';
import App from './App.vue';

import Loading from "vue-loading-overlay";
import BootstrapVue from 'bootstrap-vue'


Vue.use(Loading);
Vue.use(BootstrapVue);
Vue.config.productionTip = false;

new Vue({
  render: h => h(App)
}).$mount('#app');
