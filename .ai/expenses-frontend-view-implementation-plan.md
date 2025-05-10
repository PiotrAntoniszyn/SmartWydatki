# Plan implementacji widoku Lista wydatków (/expenses)

## 1. Przegląd
Widok umożliwia użytkownikowi zarządzanie listą wydatków: przeglądanie, filtrowanie (opis, data, kwota), paginację (20/strona) oraz operacje CRUD (dodaj/edytuj/usuwaj) w modalu. Cel: szybki, intuicyjny dostęp do danych i aktualizacji wydatków.

## 2. Routing widoku
Ścieżka: `/expenses` (Flask: `@app.route('/expenses')` lub blueprint 'expenses', metoda GET renderuje szablon Jinja2 `expenses.html`).

## 3. Struktura komponentów
- ExpensesView (Jinja2 template `expenses.html`)
  - FilterPanelModal (Bootstrap modal)
  - ExpenseFormModal (Bootstrap modal)
  - ErrorDialog (Bootstrap modal)
  - LoadingSpinner (blok overlay + spinner)
  - ContentContainer
    - EmptyState (jeśli brak wydatków)
    - ExpensesTable (HTML `<table>`)
  - PaginationControls (prev/next + info o stronie)

## 4. Szczegóły komponentów

### 4.1 ExpensesView
- Opis: główny wrapper, inicjuje JS, trzyma kontenery.
- Elementy: `<div id="expenses-app">`, placeholdery na modale i spinner.
- Zdarzenia: `DOMContentLoaded` → initExpensesApp()
- Walidacja: brak.
- Typy: żadnych.
- Propsy: brak.

### 4.2 FilterPanelModal
- Opis: formularz filtrów: `search`, `date_from`, `date_to`, `amount_min`, `amount_max`.
- HTML: Bootstrap modal z formularzem:
  - `<input type="text" id="filter-search">`
  - `<input type="date" id="filter-date-from">`, `<input type="date" id="filter-date-to">`
  - `<input type="number" step="0.01" min="0" id="filter-amount-min">`, `<input id="filter-amount-max">`
  - Przyciski `Zastosuj`, `Resetuj`.
- Interakcje: 
  - `click Zastosuj` → walidacja dat i kwot → emit `applyFilters`.
  - `click Resetuj` → czyści pol, emit `resetFilters`.
- Walidacja:
  - dateFrom ≤ dateTo
  - amountMin ≤ amountMax, ≥0, format 2 dec
- Typy:
  - `FilterParams { search:string, dateFrom:string|null, dateTo:string|null, amountMin:number|null, amountMax:number|null }`
- Propsy: początkowe `FilterParams` przekazane z ExpensesView.

### 4.3 ExpenseFormModal
- Opis: formularz add/edit wydatku.
- HTML: Bootstrap modal z polami:
  - `<input type="number" id="expense-amount" step="0.01" min="0.01" required>`
  - `<input type="text" id="expense-description" maxlength="100">`
  - `<select id="expense-category">` (opcjonalnie, po przejściu onboardingu default istnieje)
  - Przyciski `Zapisz`, `Anuluj`.
- Interakcje:
  - `openAdd` → pusty formularz
  - `openEdit(expense)` → prefill
  - `submit` → walidacja inline (HTML5 + custom JS) → emit `saveExpense` z danymi
  - `click Anuluj` → `closeModal`
- Walidacja:
  - amount >0, ≤2 dec, required
  - description ≤100 zn.
  - category_ID wymagany (może mieć default)
- Typy:
  - `ExpenseVM { id?:string, amount:number, description:string, categoryId:string, date:string (yyyy-MM-dd) }`
- Propsy:
  - `mode: 'add'|'edit'`, `expense?:ExpenseVM`, `categories: CategoryVM[]`

### 4.4 ExpensesTable
- Opis: renderuje listę wydatków w tabeli
- HTML: `<table class="table">` nagłówki: Data, Opis, Kwota, Kategoria, Akcje
- Interakcje:
  - `click Edit` → `openEdit`
  - `click Delete` → `openDeleteConfirm(expenseId)`
- Walidacja: brak
- Typy:
  - `ExpenseVM[]`
- Propsy: `expenses: ExpenseVM[]`

### 4.5 EmptyState
- Opis: gdy `expenses.length===0`
- Elementy: komunikat „Lista jest pusta” + `<button id="add-expense">Dodaj wydatek</button>`
- Interakcje: click `add-expense` → `openAdd`

### 4.6 PaginationControls
- Opis: prev/next przyciski + informacja `strona X z Y`
- HTML: `<button id="prev-page">Poprzednia</button> <span>...</span> <button id="next-page">Następna</button>`
- Interakcje: click → emit `changePage(newOffset)`
- Typy: `PaginationVM { limit:number, offset:number, total:number, currentPage:number, totalPages:number }`
- Propsy: `pagination:PaginationVM`

### 4.7 LoadingSpinner
- Opis: overlay z spinnerem przy ładowaniu
- HTML: `<div id="loading-spinner" class="d-none">…</div>`
- Interakcje: show/hide przez JS
- Propsy: brak

### 4.8 ErrorDialog
- Opis: modal z komunikatem błędu i `Retry`
- HTML: Bootstrap modal
- Interakcje: click `Retry` → emit `retryFetch`, `close`
- Typy: brak
- Propsy: `message:string`

## 5. Typy
```ts
interface ExpenseVM {
  id: string;
  amount: number;
  description: string;
  categoryId: string;
  date: string; // 'DD/MM/YYYY'
  datetime: string; // ISO
  createdAt: string; // ISO
}
interface FilterParams {
  search: string;
  dateFrom: string | null; // ISO
  dateTo: string | null;
  amountMin: number | null;
  amountMax: number | null;
}
interface PaginationVM {
  limit: number;
  offset: number;
  total: number;
  currentPage: number;
  totalPages: number;
}
```

## 6. Zarządzanie stanem
- Centralny moduł JS `expenses.js` z obiektem state:
  - state.expenses, state.filterParams, state.pagination, state.loading, state.error, state.selectedExpense, state.isEditing
- Funkcje mutujące state i re-renderujące odpowiednie komponenty.
- Brak custom hooków – moduł JS.

## 7. Integracja API
- `fetchExpenses(params:FilterParams & {limit,offset}):Promise<{data:ExpenseDTO[],pagination}>`
- `createExpense(data):POST /expenses`
- `updateExpense(id,data):PUT /expenses/:id`
- `deleteExpense(id):DELETE /expenses/:id`
- Po każdej mutacji ponownie fetchExpenses(state.filterParams).
- Parsowanie JSON do `ExpenseVM` (format daty).

## 8. Interakcje użytkownika
1. Wejście na `/expenses` → init → fetchExpenses({},{limit:20,offset:0}) → show spinner → render ExpensesTable lub EmptyState + PaginationControls.
2. Klik `Filtruj` → otwarcie FilterPanelModal → wypełnienie → `Zastosuj` → walidacja → update filterParams → fetchExpenses.
3. Klik `Resetuj` → czyszczenie filterParams → fetchExpenses.
4. Klik `Dodaj wydatek` → otwarcie ExpenseFormModal tryb add → walidacja inline → `Zapisz` → createExpense → close modal → fetchExpenses.
5. Klik `Edytuj` przy wierszu → otwarcie ExpenseFormModal fill → submit → updateExpense → fetchExpenses.
6. Klik `Usuń` → confirm dialog → deleteExpense → fetchExpenses.
7. Klik Prev/Next → update offset → fetchExpenses.

## 9. Warunki i walidacja
- dateFrom ≤ dateTo
- amountMin ≥0, ≤ amountMax
- kwota >0, max 2 dec → `<input step="0.01" pattern="^\\d+(\\.\\d{1,2})?$" required>`
- opis maxlength=100
- categoryId required

## 10. Obsługa błędów
- Błąd fetch → ErrorDialog z message → `Retry` → ponów fetch
- Błąd 400 przy create/update → pokaż inline near pole lub alert w modal
- Błąd 404 przy delete/edit → toast „Wydatek nie znaleziony”

## 11. Kroki implementacji
1. Utwórz szablon Jinja2 `templates/expenses.html` z kontenerem i include CSS/JS.
2. Zaimplementuj makra/fragmenty HTML dla każdego komponentu.
3. Stwórz plik `static/js/expenses.js` i moduły pomocnicze (api.js, table.js, modals.js, validation.js).
4. Przy użyciu `expenses.js` załaduj stan i wykonaj `fetchExpenses` przy inicjalizacji.
5. Skonfiguruj Event Listeners dla FilterPanelModal, ExpenseFormModal, PaginationControls.
6. Dodaj spinner i ErrorDialog, z mappingiem eventów.
7. Przetestuj wszystkie interakcje manualnie i napisz proste testy e2e (opcjonalnie).
8. Dodaj responsywne style przy pomocy Bootstrap grid.
9. Upewnij się, że focus trap działa w modalu (Bootstrap domyślnie).
10. Przeprowadź code review i optymalizację. 