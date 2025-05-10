# Plan implementacji widoków Dashboard, Categories oraz Expenses

## 1. Przegląd
Dokument opisuje szczegółowy plan wdrożenia brakujących (lub niepełnych) widoków w aplikacji SmartWydatki:

1. **/categories** – kompletny widok zarządzania kategoriami użytkownika.
2. **/dashboard** – rozszerzenie o sekcje tygodniowego podsumowania i porad AI.
3. **/expenses** – uzupełnienie listy wydatków o stan pusty i (opcjonalnie) widok kart mobilnych.

Celem jest zapewnienie zgodności z PRD, historyjkami oraz istniejącym stackiem (Vue 3 + Vuetify + Supabase backend).

## 2. Routing widoku
| Widok | Ścieżka | Guard | Ładowanie leniwe |
|-------|---------|-------|------------------|
| CategoriesView | `/categories` | `auth` | ✅ (kod dzielony)
| DashboardView  | `/dashboard`  | `auth` | ✅ (już istnieje – tylko import nowych komponentów)
| ExpensesView   | `/expenses`   | `auth` | ✅ (istnieje – rozbudowa komponentów)

## 3. Struktura komponentów (drzewo)
```
AppLayout
 ├─ NavigationDrawer
 ├─ <router-view>
 │   ├─ CategoriesView
 │   │   ├─ CategoriesList
 │   │   │   ├─ CategoryRow
 │   │   │   └─ EmptyState (gdy brak kategorii)
 │   │   ├─ CategoryFormModal (persistent)
 │   │   └─ DeleteCategoryConfirmDialog (persistent)
 │   ├─ DashboardView
 │   │   ├─ WeeklySummaryCard
 │   │   └─ AiTipsPanel
 │   └─ ExpensesView
 │       ├─ FilterPanelModal
 │       ├─ ExpensesTable   (desktop ≥ md)
 │       ├─ ExpensesCards   (mobile < md)
 │       ├─ EmptyState      (gdy brak wydatków)
 │       └─ ExpenseFormModal
 └─ ErrorDialog (global)
```

## 4. Szczegóły komponentów
### 4.1 CategoriesView
- **Opis**: Strona listująca kategorie oraz umożliwiająca ich CRUD.
- **Główne elementy**: `v-card` z nagłówkiem + fab „Dodaj”, tabela `CategoriesList`.
- **Zdarzenia**: `add-click`, `edit-click(id)`, `delete-click(id)`.
- **Walidacja**: delegowana do `CategoryFormModal`.
- **Typy**: `CategoryDTO`, `CategoryFormState`.
- **Propsy**: brak (dane wewnętrzne przez composable `useCategories`).

### 4.2 CategoriesList
- **Opis**: Tabela/Lista kategorii z przyciskami Edytuj/Usuń.
- **Elementy**: `v-data-table` (desktop) lub `v-list` (mobile).
- **Zdarzenia**: `edit(id)`, `delete(id)`.
- **Walidacja**: N/A.
- **Propsy**:
  - `categories: CategoryDTO[]`

### 4.3 CategoryFormModal
- **Opis**: Modal persistent dla tworzenia / edycji kategorii.
- **Elementy**: `v-dialog persistent` → `v-form` → `v-text-field` + przyciski `Zapisz` / `Anuluj`.
- **Zdarzenia**: `save(payload)`, `close`.
- **Walidacja**:
  - `name` max 30 znaków (rule),
  - unikalność (async przez API w `useCategories`).
- **Typy**: `CategoryFormPayload { name: string }`.
- **Propsy**:
  - `mode: "create" | "edit"`
  - `initial?: CategoryDTO`

### 4.4 DeleteCategoryConfirmDialog
- **Opis**: Modal potwierdzający usunięcie (persistent).
- **Zdarzenia**: `confirm`, `cancel`.
- **Propsy**: `categoryName: string`.

---

### 4.5 WeeklySummaryCard
- **Opis**: Karta podsumowania tygodniowego (suma + liczba transakcji).
- **Elementy**: `v-card` z wyraźnymi liczbami oraz ikonami.
- **Zdarzenia**: brak.
- **Walidacja**: N/A.
- **Propsy**: `summary: ExpenseSummaryDTO`.

### 4.6 AiTipsPanel
- **Opis**: Panel wyświetlający do 3 porad AI na sesję.
- **Elementy**: `v-alert` lub `v-card` w układzie kolumnowym.
- **Zdarzenia**: `retry` (w przypadku błędu AI).
- **Walidacja**: N/A.
- **Propsy**: `tips: AiTipDTO[]`, `loading: boolean`, `error: boolean`.

---

### 4.7 ExpensesCards (opcjonalnie mobile)
- **Opis**: Karty wydatków dla ekranów < `md`.
- **Elementy**: `v-card` w `v-col` grid.
- **Zdarzenia**: `edit(id)`, `delete(id)`.
- **Propsy**: `expenses: ExpenseDTO[]`.

### 4.8 EmptyState (wspólny)
- **Opis**: Komponent z ikoną + tekstem + CTA.
- **Elementy**: `v-container` center, `v-btn`.
- **Zdarzenia**: `cta-click`.
- **Propsy**:
  - `message: string`
  - `ctaLabel: string`

## 5. Typy
| Nazwa | Pola |
|-------|------|
| `CategoryDTO` | `id: string`, `name: string`, `isDefault: boolean` |
| `CategoryFormPayload` | `name: string` |
| `ExpenseDTO` | `id, amount, description, categoryId, date` |
| `ExpenseSummaryDTO` | `totalAmount: number`, `transactionCount: number` |
| `AiTipDTO` | `message: string` |
| `ApiState<T>` | `{ data?: T, loading: boolean, error?: string }` |

_Composable-specific VM typy:_
- `UseCategoriesReturn` – metody `fetch`, `create`, `update`, `remove` + `categories: ApiState<CategoryDTO[]>`.
- `UseDashboardReturn` – `summary: ApiState<ExpenseSummaryDTO>`, `tips: ApiState<AiTipDTO[]>`.

## 6. Zarządzanie stanem
- Lokalny stan per widok poprzez composables:
  - **useCategories** – trzyma listę kategorii i operacje CRUD.
  - **useDashboard** – pobiera summary & tips, posiada metody `refreshSummary` i `refreshTips` (z retry).
  - **useExpenses** (istniejący) – rozbudowa o obsługę pustego stanu.
- Globalne: `pinia` nie jest wymagane (stan niezależny, wykluczający się pomiędzy widokami).

## 7. Integracja API
| Akcja | Endpoint | Metoda | DTO request | DTO response |
|-------|----------|--------|-------------|--------------|
| Pobranie kategorii | `/categories` | GET | – | `CategoryDTO[]` |
| Utworzenie | `/categories` | POST | `{ name }` | `CategoryDTO` |
| Aktualizacja | `/categories/:id` | PUT | `{ name }` | `CategoryDTO` |
| Usunięcie | `/categories/:id` | DELETE | – | 204 |
| Weekly summary | `/expenses/summary?period=weekly` | GET | – | `ExpenseSummaryDTO` |
| AI tips | `/ai/tips?limit=3` | GET | – | `AiTipDTO[]` |
| Lista wydatków | `/expenses` | GET | query filters | `ExpenseDTO[]` + pagination |

Wywołania realizowane przez `useApi` (timeout 10 s, retry 3), z automatycznym interceptem 401.

## 8. Interakcje użytkownika
1. Klik „Dodaj kategorię” → otwiera `CategoryFormModal` → walidacja → POST → odświeżenie listy.
2. Klik „Edytuj” przy kategorii → modal w trybie `edit` → PUT.
3. Klik „Usuń” → `DeleteCategoryConfirmDialog` → DELETE.
4. Wejście na Dashboard → równoległe wywołania summary + tips.
5. Klik „Retry” w `AiTipsPanel` przy błędzie → ponowne GET `/ai/tips` (max 3 próby).
6. Wejście na Expenses z pustą listą → render `EmptyState` → CTA otwiera `ExpenseFormModal`.

## 9. Warunki i walidacja
- **Category name**: `required`, `≤30` znaków, `unique` (GET + filtr client lub 409 z backendu).
- **Modale**: `persistent` – brak zamknięcia klik-outside / ESC (US-028).
- **CTA** w pustym stanie widoczny tylko, gdy użytkownik ma prawo dodać wydatek.

## 10. Obsługa błędów
- Błędy HTTP <400 → `ErrorDialog` globalny.
- 409 przy tworzeniu/edycji kategorii → komunikat inline w `CategoryFormModal`.
- 502 z AI → panel pokazuje `error` + przycisk Retry.
- Timeout (10 s) w `useApi` → loader zastąpiony przez komunikat.
- Logika rejestrowania błędów (`log_error`) wywołana przez backend – UI przekazuje kontekst w payload (np. description w AI Retry).

## 11. Kroki implementacji
1. Założyć folder `src/views/categories` i stworzyć plik `CategoriesView.vue`.
2. Implementować composable `useCategories.ts` (fetch + CRUD + unikalność).
3. Zbudować `CategoryFormModal.vue` z walidacją reguł Vuetify.
4. Zbudować `CategoriesList.vue` → responsywny (`v-data-table` / `v-list`).
5. Dodać `DeleteCategoryConfirmDialog.vue`.
6. Dodać trasę `/categories` w `router.ts` z lazy importem.
7. W DashboardView dodać import `WeeklySummaryCard.vue` oraz `AiTipsPanel.vue`; przygotować `useDashboard.ts`.
8. Stworzyć `WeeklySummaryCard.vue` (karta z danymi) oraz `AiTipsPanel.vue` (lista porad, loader, error).
9. Rozszerzyć `useExpenses.ts` o detekcję pustej listy; dodać `EmptyState.vue` i (opcjonalnie) `ExpensesCards.vue`.
10. Zaktualizować testy jednostkowe i e2e (Vitest + Cypress) dla nowych widoków i walidacji.
11. Upewnić się, że wszystkie modale mają `persistent`, a focus trap działa.
12. Przeprowadzić ręczne testy UX na desktopie i mobile (<md).
13. Zaktualizować dokumentację README oraz Storybook (jeśli używany) o nowe komponenty. 