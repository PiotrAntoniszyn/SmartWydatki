# Plan implementacji widoku Onboardingu (/onboarding)

Plik: `.ai/onboarding-view-implementation-plan.md`

---

## 1. Przegląd
Widok Onboardingu pozwala nowemu użytkownikowi wybrać 1–5 początkowych kategorii proponowanych przez AI. Wyświetla się on po pomyślnej rejestracji i zabezpieczony jest przed nieautoryzowanym dostępem. Użytkownik nie może kontynuować, dopóki nie zaznaczy przynajmniej jednej i nie więcej niż pięciu kategorii.

## 2. Routing widoku
- Ścieżka: `/onboarding`
- Router guard: dostęp tylko gdy `isAuthenticated=true`, w przeciwnym razie `router.push('/login')`.
- Po zatwierdzeniu: `router.push('/dashboard')`.

## 3. Struktura komponentów
OnboardingView  
├─ LoadingSpinner  
├─ ErrorDialog  
├─ CategoriesSuggestionsList  
└─ v-btn „Kontynuuj”

## 4. Szczegóły komponentów

### 4.1 OnboardingView
- Opis: Kontener dla całej logiki onboardingowej, otwiera modal, steruje fetch-em i stanem.
- Główne elementy:
  - `<v-dialog persistent no-close-on-backdrop no-close-on-esc role="dialog">`
  - `<LoadingSpinner>` (gdy `loading=true` i min 200 ms)
  - `<ErrorDialog>` (gdy `errorMessage`)
  - `<CategoriesSuggestionsList>` (lista propozycji)
  - `<v-btn>` „Kontynuuj” (disabled gdy wybranych <1 lub >5)
- Obsługiwane interakcje:
  - mount → `fetchSuggestions()`
  - retry w `ErrorDialog` → ponowne `fetchSuggestions()`
  - toggle selekcji → `onToggle(id)`
  - klik „Kontynuuj” → `handleContinue()`
- Walidacja:
  - minSelected = 1, maxSelected = 5
- Typy i ViewModel:
  - suggestions: `CategorySuggestionVM[]`
  - loading: `boolean`
  - errorMessage: `string|null`
  - selectedCount: `computed<number>`
- Kompozycje/hooki:
  - `useApi()` do GET `/categories/suggestions`
  - ewentualnie `useOnboardingSuggestions()` wyciągające logikę fetch/stan

### 4.2 CategoriesSuggestionsList
- Opis: Renderuje listę elementów do wyboru.
- Główne elementy:
  - `<v-chip-group multiple max="5" v-model="selectedIds">`  
    lub `<v-checkbox>` w `<v-list-item>` dla każdego suggestion
- Props:
  - `items: CategorySuggestionVM[]`
  - `selectedIds: string[]`
- Emitowane zdarzenia:
  - `@update:selectedIds="onToggle"`
- Typy:
  - `CategorySuggestionVM { id: string; name: string; usageCount: number; }`
- Walidacja UI:
  - blokowanie wyboru ponad 5 elementów (Vuetify `max`)
  - nie pozwala odznaczyć wszystkiego (minSelected w OnboardingView)

### 4.3 LoadingSpinner
- Standardowy spinner Vuetify (komponent gotowy).
- Wyświetlany gdy `loading=true` ponad 200 ms.

### 4.4 ErrorDialog
- `<v-dialog persistent>` z rolą alert/dialog.
- Pokazuje `errorMessage` i przycisk Retry.
- Emituje `@retry` → wywołanie fetch ponownie.

### 4.5 SubmitButton
- `<v-btn color="primary" :disabled="!isValid">Kontynuuj</v-btn>`
- Props:
  - `isValid: boolean`
- Emituje `@click="onContinue"`

## 5. Typy

```ts
// DTO z API
interface CategorySuggestionDTO {
  id: string;
  name: string;
  usage_count: number;
}

// ViewModel w komponencie
interface CategorySuggestionVM {
  id: string;
  name: string;
  usageCount: number;
}

// Hook / composable state
interface UseOnboardingSuggestions {
  suggestions: Ref<CategorySuggestionVM[]>;
  loading: Ref<boolean>;
  errorMessage: Ref<string|null>;
  selectedIds: Ref<string[]>;
  fetchSuggestions(): Promise<void>;
  toggleSelection(id: string): void;
  canContinue: ComputedRef<boolean>;
}
```

## 6. Zarządzanie stanem
- Lokalny stan w Composition API (`ref`, `computed`).
- `suggestions`, `loading`, `errorMessage`, `selectedIds`.
- Computed `canContinue = selectedIds.value.length >= 1 && <= 5`.
- Optional: `useOnboardingSuggestions()` hook zawierający powyższy state + logikę fetch/toggle.

## 7. Integracja API
- Metoda: GET `/categories/suggestions`
- Nagłówek: `Authorization` (z `useApi`).
- Query params (jeśli wymagane przez backend): e.g. `?description=&amount=0` (lub `?onboarding=true` – do uzgodnienia z backendem).
- Odpowiedź 200: `CategorySuggestionDTO[]`.
- Błędy:
  - 502 → errorMessage = „Usługa niedostępna, spróbuj ponownie później.”
  - 401 → intercept `useApi` → `router.push('/login')`
  - inne 5xx → analogicznie do 502.

## 8. Interakcje użytkownika
1. Użytkownik wchodzi na `/onboarding`.
2. Dialog otwiera się automatycznie, rozpoczyna się fetch.
3. Jeśli opóźnienie >200 ms → spinner.
4. Gdy fetch zakończony:
   - success → wyświetl `CategoriesSuggestionsList`.
   - failure → `ErrorDialog`.
5. Użytkownik wybiera od 1 do 5 propozycji:
   - CLI: toggle w liście.
   - `canContinue` = true → aktywny przycisk.
6. Klik „Kontynuuj”:
   - `router.push('/dashboard')`.

## 9. Warunki i walidacja
- minSelected = 1, maxSelected = 5 (bloki wyboru i stan przycisku).
- Persistent dialog: brak zamykania ESC / backdrop.
- focus-trap: po otwarciu dialogu focus na pierwszym elemencie listy.

## 10. Obsługa błędów
- Błąd API → `ErrorDialog` z Retry.
- Brak danych (pusta lista) → komunikat „Brak propozycji kategorii” + Retry.
- 401 → `useApi` intercept → redirect do `/login`.
- Próba kliknięcia Kontynuuj poza zakresem walidacji → disabled.

## 11. Kroki implementacji
1. Utwórz plik `OnboardingView.vue` w katalogu `app/components` lub `views`.
2. Skonfiguruj router: dodaj trasę `/onboarding` z lazy-loadem i guardem `requiresAuth`.
3. W `OnboardingView.vue`:
   - zaimportuj `useApi`, `ref`, `computed`, `onMounted`, `useRouter`.
   - zainicjuj stan: `suggestions`, `loading`, `errorMessage`, `selectedIds`.
   - napisz `fetchSuggestions()` korzystając z `useApi().get('/categories/suggestions')`.
   - obsłuż błędy i loading.
   - computed `canContinue`.
   - funkcję `toggleSelection(id)`.
   - `handleContinue()` → `router.push('/dashboard')`.
4. Zaimplementuj `CategoriesSuggestionsList.vue`:
   - props `items`, `selectedIds`.
   - v-chip-group lub lista checkboxów.
5. Dodaj `LoadingSpinner` oraz `ErrorDialog` (jeśli nie istnieją).
6. Dodaj stylowanie i aria-labels (dialog, checkboxy).
7. Napisz walidację inline (tekstowe komunikaty przy invalid).
8. Przetestuj scenariusze: sukces, błąd, pusty zestaw, 401.
9. Dodaj e2e testy dla widoku `/onboarding`.
10. Zweryfikuj dostępność (a11y).

---

*Plan zgodny z PRD, User Stories i istniejącym stackiem Vue 3 + Vuetify + Composition API.* 