import { createRouter, createWebHashHistory } from "vue-router";
import home from "../pages/home.vue";
import playground from "../pages/playground.vue";
import notFound from "../pages/notFound.vue";

const routes = [
  {
    path: "/",
    name: "home",
    component: home,
  }, {
    path: "/playground",
    name: "playground",
    component: playground,
  }, {
    path: "/:catchAll(.*)",
    name: "notFound",
    component: notFound,
  },
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
});

export default router;