/* import MainView from "@/views/MainView.vue"; */
import { createRouter, createWebHistory } from "vue-router";
import StatsView from "@/views/StatsView.vue";
import SplitView from "@/views/SplitView.vue";


const routes = [
  { path: "/Home", component: SplitView, alias: "/" },
  { path: "/Interpretability/:name", component: StatsView },
  /* { path: "/old", component: MainView }, */
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;