import { createI18n } from "vue-i18n";

export default createI18n({
  legacy: false,
  locale: "en",
  fallbackLocale: "pl",
  globalInjection: true,
  messages: {
    en: require("@/lang/en-US.json"),
    pl: require("@/lang/pl-PL.json")
  }
});
