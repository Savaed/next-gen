import { createApp } from "vue";
import App from "@/App.vue";
import router from "@/router";
import store from "@/store";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
// import vuelidate from "@/plugins/vuelidate.js";
import i18n from "@/plugins/i18n.js";
import vuetify from "@/plugins/vuetify.js";

const app = createApp(App);

app.component("font-awesome-icon", FontAwesomeIcon);

app.use(vuetify);
app.use(i18n);
// app.use(vuelidate);
app.use(router);
app.use(store);

app.mount("#app");
