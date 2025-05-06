<template>
  <div class="dashboard-container">
    <v-app-bar color="primary" dark>
      <v-app-bar-nav-icon @click="drawer = !drawer"></v-app-bar-nav-icon>
      <v-toolbar-title>Dashboard</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn icon @click="auth.logout()" aria-label="Wyloguj się">
        <v-icon>mdi-logout</v-icon>
      </v-btn>
    </v-app-bar>

    <v-navigation-drawer
      v-model="drawer"
      app
      temporary
    >
      <v-list>
        <v-list-item>
          <v-list-item-content>
            <v-list-item-title class="text-h6">
              Aplikacja budżetowa
            </v-list-item-title>
          </v-list-item-content>
        </v-list-item>

        <v-divider></v-divider>

        <v-list-item
          v-for="item in menuItems"
          :key="item.title"
          link
          :to="item.path"
        >
          <v-list-item-icon>
            <v-icon>{{ item.icon }}</v-icon>
          </v-list-item-icon>

          <v-list-item-content>
            <v-list-item-title>{{ item.title }}</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>

    <v-main>
      <v-container>
        <v-row>
          <v-col cols="12">
            <v-card>
              <v-card-title class="text-h5">
                Witaj w aplikacji budżetowej!
              </v-card-title>
              <v-card-text>
                <p>Onboarding został zakończony pomyślnie. Wybrane kategorie zostały zapisane.</p>
                <p>To jest przykładowy Dashboard. W rzeczywistej implementacji, ten widok zawierałby dalsze komponenty i funkcjonalności.</p>
              </v-card-text>
            </v-card>
          </v-col>
          
          <v-col cols="12" md="6">
            <v-card>
              <v-card-title>Ostatnie wydatki</v-card-title>
              <v-card-text>
                <p>Tutaj będzie wyświetlona lista ostatnich wydatków.</p>
              </v-card-text>
            </v-card>
          </v-col>
          
          <v-col cols="12" md="6">
            <v-card>
              <v-card-title>Statystyki</v-card-title>
              <v-card-text>
                <p>Tutaj będą wyświetlone statystyki wydatków.</p>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuth } from '../composables/useAuth';

const router = useRouter();
const auth = useAuth();
const drawer = ref(false);

// Menu items for the navigation drawer
const menuItems = [
  { title: 'Dashboard', icon: 'mdi-view-dashboard', path: '/dashboard' },
  { title: 'Wydatki', icon: 'mdi-currency-usd', path: '/expenses' },
  { title: 'Kategorie', icon: 'mdi-shape', path: '/categories' },
  { title: 'Ustawienia', icon: 'mdi-cog', path: '/settings' }
];
</script>

<style scoped>
.dashboard-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}
</style> 