# Architektura UI dla SmartWydatki

## 1. Przegląd struktury UI
SmartWydatki to jednostronicowa aplikacja (SPA) zbudowana w Vue 3 (Composition API), wykorzystująca Vuetify (dark theme) i Vue Router. Aplikacja dzieli się na dwa główne moduły:
- **Auth**: logowanie, rejestracja, onboarding
- **App**: dashboard, lista wydatków, zarządzanie kategoriami, ustawienia

Nawigacja odbywa się za pomocą **sidebar** na desktopie oraz **hamburger menu** na urządzeniach mobilnych. Komunikacja z API realizowana jest przez composable `useApi`, który zapewnia:
- natywny `fetch` z timeoutem 10 s i retry do 3 razy
- intercept 401 → automatyczne przekierowanie do `/login`
- cache w pamięci aplikacji (do restartu)

Formularze modalne korzystają z komponentu `v-dialog` (persistent) z focus trapping i ARIA role. Stany ładowania i błędów obsługują `LoadingSpinner` i `ErrorDialog`.

## 2. Lista widoków

### 2.1. Logowanie
- Ścieżka: `/login`
- Cel: uwierzytelnienie użytkownika
- Kluczowe informacje: pola `E-mail`, `Hasło` (min 8 znaków), walidacja inline, przyciski `Zaloguj` i link do rejestracji
- Kluczowe komponenty: `AuthForm`, `LoadingSpinner`, `ErrorDialog`
- UX/dostępność/bezpieczeństwo:
  - focus na pierwszym polu
  - `aria-label` dla pól formularza
  - token w httpOnly cookie

### 2.2. Rejestracja
- Ścieżka: `/register`
- Cel: utworzenie nowego konta
- Kluczowe informacje: pola `E-mail`, `Hasło`, `Potwierdź hasło`, walidacja (min 8 znaków, matching), komunikaty inline
- Kluczowe komponenty: `AuthForm`, `LoadingSpinner`, `ErrorDialog`
- UX/dostępność/bezpieczeństwo: analogiczne do widoku logowania

### 2.3. Onboarding
- Ścieżka: `/onboarding`
- Cel: wybór 3–5 początkowych kategorii sugerowanych przez AI
- Kluczowe informacje:
  - lista `CategoriesSuggestionsList` z propozycjami z `GET /categories/suggestions`
  - walidacja wyboru 1–5 kategorii
  - przycisk `Kontynuuj`
- Kluczowe komponenty: `CategoriesSuggestionsList`, `ErrorDialog`
- UX/dostępność/bezpieczeństwo:
  - wyświetlenie w `v-dialog` persistent (focus trap, role="dialog")
  - obsługa błędów API i retry

### 2.4. Dashboard
- Ścieżka: `/dashboard`
- Cel: podsumowanie tygodniowe i porady AI
- Kluczowe informacje:
  - `WeeklySummaryCard` (dane z `GET /expenses/summary`)
  - `AiTipsPanel` (dane z `GET /ai/tips`, limit=3)
- Kluczowe komponenty: `WeeklySummaryCard`, `AiTipsPanel`, `LoadingSpinner`, `ErrorDialog`
- UX/dostępność/bezpieczeństwo:
  - dynamiczna aktualizacja z `aria-live`
  - loader podczas oczekiwania
  - prezentacja stanu błędu (AI/service)

### 2.5. Lista wydatków
- Ścieżka: `/expenses`
- Cel: przegląd, filtrowanie i zarządzanie wydatkami (CRUD)
- Kluczowe informacje:
  - `ExpensesTable` lub `ExpensesCards` z paginacją (limit 20, prev/next)
  - filtry: `search`, `date_from`, `date_to`, `amount_min`, `amount_max`
  - CRUD przez `ExpenseFormModal` (v-dialog)
- Kluczowe komponenty: `ExpensesTable`, `ExpenseFormModal`, `FilterPanelModal`, `PaginationControls`, `LoadingSpinner`, `ErrorDialog`, `EmptyState`
- UX/dostępność/bezpieczeństwo:
  - domyślne sortowanie malejąco po dacie
  - walidacja inline w formularzu
  - focus trap w modalach

### 2.6. Zarządzanie kategoriami
- Ścieżka: `/categories`
- Cel: CRUD kategorii użytkownika
- Kluczowe informacje:
  - `CategoriesList` z przyciskami Dodaj/Edycja/Usuń
  - walidacja nazwy (unikalność, max 30 znaków)
- Kluczowe komponenty: `CategoriesList`, `CategoryFormModal`, `LoadingSpinner`, `ErrorDialog`, `EmptyState`
- UX/dostępność/bezpieczeństwo:
  - inline validation
  - confirm dialog przy usuwaniu
  - focus trapping

### 2.7. Ustawienia
- Ścieżka: `/settings`
- Cel: zmiana hasła i usunięcie konta
- Kluczowe informacje:
  - `PasswordChangeForm` (stare hasło, nowe hasło, potwierdź)
  - `DeleteAccountSection` z `DeleteAccountDialog` (confirm)
- Kluczowe komponenty: `PasswordChangeForm`, `DeleteAccountDialog`, `LoadingSpinner`, `ErrorDialog`
- UX/dostępność/bezpieczeństwo:
  - dialog potwierdzający usunięcie konta
  - mocna walidacja haseł

## 3. Mapa podróży użytkownika
1. Wejście na `/login`.
2. (Nowy) Przejście do `/register` → rejestracja → przekierowanie do `/onboarding`.
3. Wybór kategorii (1–5) → `Kontynuuj` → `/dashboard`.
4. Dashboard: przegląd podsumowania i AI tips.
5. Nawigacja do `/expenses` → filtrowanie/wyszukiwanie → CRUD wydatków w modalach → powrót do listy.
6. (Opcjonalnie) `/categories` → zarządzanie kategoriami.
7. `/settings` → zmiana hasła lub usunięcie konta → logout → `/login`.

## 4. Układ i struktura nawigacji
- **Desktop**: stały `NavigationDrawer` z linkami do `Dashboard`, `Wydatki`, `Kategorie`, `Ustawienia`, `Wyloguj`.
- **Mobile**: hamburger menu otwierające `NavigationDrawer` jako overlay.
- **Router Guards**: ochrona tras `auth` i `app`; intercept 401 w `useApi` → `router.push('/login')`.
- **Breadcrumbs/Context**: nagłówki widoków ze wskazaniem aktualnej sekcji.

## 5. Kluczowe komponenty
- `useApi`: composable do fetch z timeoutem, retry, intercept 401, cache w pamięci
- `AuthForm`: formularz logowania i rejestracji z walidacją
- `ExpenseFormModal`: modal CRUD wydatków (v-dialog)
- `CategoryFormModal`: modal CRUD kategorii (v-dialog)
- `WeeklySummaryCard`: karta podsumowania tygodniowego
- `AiTipsPanel`: panel z poradami AI
- `LoadingSpinner`: komponent loadera
- `ErrorDialog`: komponent modalny do błędów i retry
- `PaginationControls`: kontrolki paginacji
- `FilterPanelModal`: modal filtrów w widoku wydatków
- `DrawerMenu`: komponent sidebar/hamburger navigation
- `EmptyState`: komponent widoku pustej listy 