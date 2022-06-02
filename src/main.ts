import Vue from "vue";
import App from "./App.vue";
import vuetify from "./plugins/vuetify";
import router from "./plugins/router";
import store from "@/plugins/vuex";
import "@/plugins/highlight";
import DatetimePicker from "vuetify-datetime-picker";

Vue.config.productionTip = false;

Vue.use(DatetimePicker);

new Vue({
  vuetify,
  router,
  store,
  render(h) { return h(App); },
}).$mount("#app");
