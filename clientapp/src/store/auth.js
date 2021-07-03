const TOKEN_KEY = "user-access-token";
const USER_ROLES_KEY = "user-roles";

const authModule = {
  namespaced: true,
  state: {
    accessToken: localStorage.getItem(TOKEN_KEY) || "",
    userRoles: localStorage.getItem(USER_ROLES_KEY) || []
  },

  mutations: {
    SET_ACCESS_TOKEN(state, token) {
      localStorage.setItem(TOKEN_KEY, token);
      state.accessToken = token;
    },
    REMOVE_ACCESS_TOKEN(state) {
      localStorage.removeItem(TOKEN_KEY);
      state.accessToken = "";
    },
    SET_USER_ROLES(state, roles) {
      localStorage.setItem(USER_ROLES_KEY, JSON.stringify(roles));
      state.userRoles = roles;
    },
    REMOVE_USER_ROLES(state) {
      localStorage.removeItem(USER_ROLES_KEY);
      state.userRoles = [];
    }
  },

  actions: {
    setAccessToken({ commit }, token) {
      if (token) {
        commit("SET_ACCESS_TOKEN", token);
      }
    },
    removeAccessToken({ commit }) {
      commit("REMOVE_ACCESS_TOKEN");
    },
    setUserRoles({ commit }, roles) {
      if (roles && roles.length > 0) {
        commit("SET_USER_ROLES", roles);
      }
    },
    removeUserRoles({ commit }) {
      commit("REMOVE_USER_ROLES");
    }
  },

  getters: {
    userAccessToken(state) {
      return state.accessToken;
    },
    userRoles(state) {
      return JSON.parse(JSON.stringify(state.userRoles));
    }
  }
};

export default authModule;
