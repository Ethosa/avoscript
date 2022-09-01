import { createRouter, createWebHashHistory } from "vue-router"
import home from "../pages/home.vue"
import playground from "../pages/playground.vue"
import notFound from "../pages/notFound.vue"
import packagesList from "../pages/packagesList.vue"
import packageInfo from "../pages/packageInfo.vue"

const routes = [
  {
    path: "/",
    name: "home",
    component: home,
  }, {
    path: "/code/:uuid",
    name: "loadCode",
    component: playground,
  }, {
    path: "/playground",
    name: "playground",
    component: playground,
  }, {
    path: "/packages",
    name: "packages",
    component: packagesList,
  }, {
    path: "/package/:name",
    name: "packageInfo",
    component: packageInfo,
  }, {
    path: "/:catchAll(.*)",
    name: "notFound",
    component: notFound,
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

export default router