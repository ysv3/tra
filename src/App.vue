<template>
  <v-app>
  <span> Welcome</span>
  <v-content>
    <router-view/> 
  </v-content>
  </v-app>
</template>

<script lang="ts">
import Vue from "vue";

export default Vue.extend({
  name: "App",
  components: {},
  data: () => ({
  }),
  computed: {
    routes(): Array<{
      name: string;
      route: string;
      icon: string;
    }> {
      // Add routes here to correspond to router.ts
      return [
        {
          name: "Home",
          route: "/",
          icon: "mdi-home-variant",
        }
      ];
    },
  }
});
</script>
