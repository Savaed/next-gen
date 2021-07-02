import { createVuetify } from "vuetify";
import { aliases, fa } from "vuetify/lib/iconsets/fa-svg";
import { library } from "@fortawesome/fontawesome-svg-core";
import { fas } from "@fortawesome/free-solid-svg-icons";
import { far } from "@fortawesome/free-regular-svg-icons";

library.add(fas);
library.add(far);

export default createVuetify({
  icons: {
    defaultSet: "fa",
    aliases,
    sets: {
      fa
    }
  }
  // theme: {
  //   defaultTheme: "customDarkTheme",
  //   themes: {
  //     customDarkTheme: {
  //       dark: true
  //       colors: {}
  //     }
  //   }
  // }
});
