import axios from "axios";
import { useStore } from "vuex";

const BASE_URL = "https://localhost:8000/api";

const apiAxios = axios.create({
  headers: {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*"
  },
  timeout: 120000
});

function createHeaders() {
  const token = useStore().getters["auth/userAccessToken"];

  if (token) {
    return {
      Authorization: token
    };
  }
}

apiAxios.interceptors.request.use(
  request => {
    request.headers = createHeaders();
    return request;
  },
  error => {
    /* eslint-disable  no-console */
    console.log(error);
  }
);

export { apiAxios, BASE_URL };
