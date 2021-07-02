import { createApp } from "vue";
import vuetify from "@/plugins/vuetify.js";
import App from "@/App.vue";
import router from "@/router";
import store from "@/store";
import i18n from "@/plugins/i18n.js";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";

const app = createApp(App);

app.component("font-awesome-icon", FontAwesomeIcon);

app.use(vuetify);
app.use(i18n);
app.use(router);
app.use(store);

app.mount("#app");
