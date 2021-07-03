import { createStore } from "vuex";
import authModule from "@/store/auth.js";

export default createStore({
  state: {},
  mutations: {},
  actions: {},
  modules: {
    auth: authModule
  }
});
