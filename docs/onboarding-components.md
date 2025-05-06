# Dokumentacja komponentów Onboardingu

## Przegląd

Moduł onboardingu pozwala nowym użytkownikom wybrać od 1 do 5 kategorii po rejestracji/logowaniu. 
Widok ten jest zabezpieczony przed nieautoryzowanym dostępem i wymaga uwierzytelnienia.

## Komponenty

### OnboardingView

**Plik:** `app/static/js/views/OnboardingView.vue`

**Opis:** Główny kontener dla całej logiki onboardingowej. Jest to pełnoekranowy dialog, który uniemożliwia dostęp do innych części aplikacji przed wybraniem kategorii.

**Główne funkcje:**
- Pełnoekranowy dialog, który nie może zostać zamknięty
- Obsługa stanu ładowania i błędów
- Renderowanie listy sugerowanych kategorii
- Walidacja wyboru (min 1, max 5 kategorii)
- Przycisk "Kontynuuj" do zakończenia procesu

**Zależności:**
- `LoadingSpinner`
- `ErrorDialog`
- `CategoriesSuggestionsList`
- `useOnboardingSuggestions` - composable do zarządzania stanem i pobierania danych

**Stan:**
```ts
const {
  suggestions,     // Lista sugestii kategorii
  loading,         // Stan ładowania
  errorMessage,    // Komunikat błędu
  selectedIds,     // IDs wybranych kategorii
  fetchSuggestions, // Funkcja do pobierania sugestii
  canContinue      // Czy można kontynuować (computed)
} = useOnboardingSuggestions();
```

**Dostępność (a11y):**
- Poprawnie zdefiniowane role ARIA (dialog, alert)
- Etykiety dla przycisków
- Zarządzanie fokusem (focus-trap w dialogu)

### CategoriesSuggestionsList

**Plik:** `app/static/js/components/CategoriesSuggestionsList.vue`

**Opis:** Komponent renderujący listę sugerowanych kategorii do wyboru w formie chipów.

**Props:**
```ts
const props = defineProps<{
  items: CategorySuggestionVM[];  // Sugerowane kategorie
  selectedIds: string[];         // IDs wybranych kategorii
}>();
```

**Emitowane zdarzenia:**
```ts
const emit = defineEmits<{
  'update:selectedIds': [selectedIds: string[]]; // Aktualizacja wybranych ID
}>();
```

**Główne funkcje:**
- Renderowanie listy kategorii jako chipów Vuetify
- Obsługa wyboru kategorii (toggle)
- Walidacja limitu wyboru (max 5)
- Wyświetlanie licznika wybranych elementów

**Dostępność (a11y):**
- Dynamiczne etykiety ARIA dla stanu wyboru
- Obsługa klawiatury
- Komunikaty o ograniczeniach wyboru

### ErrorDialog

**Plik:** `app/static/js/components/ErrorDialog.vue`

**Opis:** Komponent dialogu wyświetlającego komunikaty błędów z możliwością ponowienia akcji.

**Props:**
```ts
const props = defineProps<{
  message: string | null; // Komunikat błędu
}>();
```

**Emitowane zdarzenia:**
```ts
const emit = defineEmits<{
  retry: []; // Zdarzenie ponowienia próby
}>();
```

**Główne funkcje:**
- Wyświetlanie komunikatu błędu
- Przycisk "Spróbuj ponownie"
- Automatyczne pokazywanie/ukrywanie w zależności od stanu błędu

**Dostępność (a11y):**
- Rola alertdialog
- Poprawne etykiety i komunikaty

### LoadingSpinner

**Plik:** `app/static/js/components/LoadingSpinner.vue`

**Opis:** Prosty komponent loadera wykorzystujący Vuetify Progress Circular.

**Główne funkcje:**
- Animacja ładowania
- Komunikat tekstowy

**Dostępność (a11y):**
- Rola status
- aria-live="polite" dla czytników ekranu
- Tekstowa informacja o stanie ładowania

## Composables (Hooki)

### useOnboardingSuggestions

**Plik:** `app/static/js/composables/useOnboardingSuggestions.ts`

**Opis:** Hook zarządzający stanem i logiką onboardingu.

**Interfejs:**
```ts
interface UseOnboardingSuggestions {
  suggestions: Ref<CategorySuggestionVM[]>; // Lista sugestii
  loading: Ref<boolean>;                    // Stan ładowania
  errorMessage: Ref<string|null>;           // Komunikat błędu
  selectedIds: Ref<string[]>;               // Wybrane IDs
  fetchSuggestions: () => Promise<void>;    // Funkcja pobierania
  toggleSelection: (id: string) => void;    // Przełączanie wyboru
  canContinue: ComputedRef<boolean>;        // Czy można kontynuować
}
```

**Główne funkcje:**
- Pobieranie sugestii kategorii z API
- Zarządzanie stanem ładowania i błędów
- Obsługa wyboru kategorii (dodawanie/usuwanie)
- Walidacja (min 1, max 5 wyborów)

### useAuth

**Plik:** `app/static/js/composables/useAuth.ts`

**Opis:** Hook zarządzający autentykacją użytkownika.

**Interfejs:**
```ts
{
  isAuthenticated: ComputedRef<boolean>;    // Czy użytkownik jest zalogowany
  loading: Ref<boolean>;                    // Stan ładowania
  error: Ref<string | null>;                // Komunikat błędu
  login: (email: string, password: string) => Promise<boolean>; // Logowanie
  register: (userData: {...}) => Promise<boolean>;              // Rejestracja
  logout: () => void;                       // Wylogowanie
  requireAuth: () => boolean;               // Sprawdzenie auth i przekierowanie
}
```

**Główne funkcje:**
- Logowanie i rejestracja użytkownika
- Zarządzanie tokenem uwierzytelniającym
- Wylogowywanie
- Sprawdzanie stanu uwierzytelnienia

## Routing

Ścieżka: `/onboarding`

**Konfiguracja:**
```ts
{
  path: '/onboarding',
  name: 'Onboarding',
  component: () => import('../views/OnboardingView.vue'),
  meta: {
    requiresAuth: true,
    title: 'Onboarding - Wybierz kategorie'
  }
}
```

Router zawiera guard, który przekierowuje nieuwierzytelnionych użytkowników do strony logowania.

## Typy danych

**CategorySuggestionDTO:** Typ danych przychodzących z API
```ts
interface CategorySuggestionDTO {
  id: string;
  name: string;
  usage_count: number;
}
```

**CategorySuggestionVM:** Model widoku używany w komponentach
```ts
interface CategorySuggestionVM {
  id: string;
  name: string;
  usageCount: number;
}
```

## Integracja z API

- **Endpoint:** `GET /categories/suggestions`
- **Parametry:** `{ onboarding: true }`
- **Autoryzacja:** Token w nagłówku
- **Odpowiedź:** Lista sugerowanych kategorii
- **Obsługa błędów:** Komunikaty dla 401, 502 i innych błędów

## Testy E2E

Testy znajdują się w pliku: `tests/e2e/onboarding.spec.ts`

Główne scenariusze testowe:
1. Przekierowanie do onboardingu po zalogowaniu
2. Wybór kategorii i walidacja liczby wyborów
3. Obsługa błędów API
4. Nawigacja za pomocą klawiatury (dostępność)

## Uwagi implementacyjne

1. **Dostępność (a11y):**
   - Zastosowano poprawne role ARIA
   - Zaimplementowano obsługę klawiatury
   - Dodano odpowiednie etykiety i komunikaty

2. **Bezpieczeństwo:**
   - Guard routera chroni przed nieautoryzowanym dostępem
   - Walidacja po stronie klienta i serwera

3. **Rozbudowa:**
   - Aby dodać nowe kategorie, wystarczy zaktualizować backend
   - Aby zmienić limity wyborów, należy zaktualizować kod w `useOnboardingSuggestions`
   - Dodatkowe style można dostosować w komponentach 