# Plan implementacji widoku Zarządzanie kategoriami

## 1. Przegląd
Widok Zarządzanie kategoriami umożliwia użytkownikowi przegląd, dodawanie, edycję i usuwanie własnych kategorii wydatków. Całość odbywa się w formie responsywnej strony z modalami, z inline walidacją i potwierdzeniami.

## 2. Routing widoku
Ścieżka: `/categories`

## 3. Struktura komponentów
- `CategoriesPage`
  - `LoadingSpinner`
  - `ErrorDialog`
  - warunek pustej listy → `EmptyState`
  - `CategoriesList`
  - `CategoryFormModal` (dodawanie/edycja)
  - `ConfirmDialog` (usuwanie)

## 4. Szczegóły komponentów

### CategoriesPage
- Opis: główny kontener widoku, odpowiedzialny za ładowanie danych i zarządzanie stanem modali.
- Główne elementy: kontener listy, przycisk `Zarządzaj kategoriami`/`Dodaj kategorię`.
- Obsługiwane interakcje:
  - mount → fetch `/categories`
  - klik `Dodaj kategorię` → otwarcie `CategoryFormModal` (tryb dodawania)
  - klik `Edytuj` przy elemencie → otwarcie `CategoryFormModal` (tryb edycji z wypełnionym polem)
  - klik `Usuń` → otwarcie `ConfirmDialog`
- Typy:
  - ViewModel: `CategoryListItem { id: string; name: string; is_default: boolean; }`
- Propsy: brak (root view)

### LoadingSpinner
- Opis: wyświetlany gdy trwa ładowanie lub operacja sieciowa (>200ms)
- Główne elementy: ikona spinnera, opcjonalny komunikat
- Propsy: `visible: boolean`

### ErrorDialog
- Opis: modal pokazujący komunikat błędu operacji sieciowej
- Główne elementy: tytuł, tekst błędu, przycisk `OK`
- Propsy: `message: string`, `onClose: () => void`

### EmptyState
- Opis: widok gdy lista kategorii jest pusta
- Główne elementy: komunikat „Lista jest pusta”, przycisk `Dodaj kategorię`
- Propsy: `onAdd: () => void`

### CategoriesList
- Opis: tabela/siatka kategorii z akcjami
- Główne elementy:
  - lista pozycji: nazwa, oznaczenie default (readonly)
  - przyciski `Edytuj`, `Usuń` przy każdym elemencie
- Zdarzenia:
  - `onEdit(id)`
  - `onDelete(id)`
- Propsy:
  - `categories: CategoryListItem[]`
  - `onEdit: (id: string) => void`
  - `onDelete: (id: string) => void`

### CategoryFormModal
- Opis: modal formularza do dodawania/edycji kategorii
- Główne elementy:
  - pole tekstowe `Nazwa kategorii`
  - przyciski `Zapisz`, `Anuluj`
- Obsługiwane interakcje:
  - focus trap → focus w polu nazwy przy otwarciu
  - walidacja inline na długość (<=30)
  - opcjonalna walidacja unikalności (po stronie klienta porównanie z lokalną listą)
  - submit → POST lub PUT
- Warunki walidacji:
  - niepuste
  - max 30 znaków
  - unikalna w lokalnym stanie listy
- Typy:
  - `CategoryFormData { id?: string; name: string; }`
- Propsy:
  - `mode: 'create' | 'edit'`
  - `initialData?: CategoryFormData`
  - `onSave: (data: CategoryFormData) => Promise<void>`
  - `onCancel: () => void`

### ConfirmDialog
- Opis: modal potwierdzający usunięcie kategorii
- Główne elementy: tekst „Czy na pewno chcesz usunąć kategorię?”, przyciski `OK`/`Anuluj`
- Propsy:
  - `message: string`
  - `onConfirm: () => Promise<void>`
  - `onCancel: () => void`

## 5. Typy
- CategoryListItem
  - `id: string`
  - `name: string`
  - `is_default: boolean`
- CategoryFormData
  - `id?: string`
  - `name: string`

## 6. Zarządzanie stanem
- `useCategories()`
  - stan: `categories`, `loading`, `error`
  - akcje: `fetchAll()`, `add(data)`, `update(data)`, `remove(id)`
- `useModal()` (opcjonalny hook do zarządzania widocznością modali)

## 7. Integracja API
- GET `/categories` → zwraca `CategoryRead[]` → przemapować na `CategoryListItem[]`
- POST `/categories` z `{ name }` → 201 → dodać do stanu
- PUT `/categories/:id` z `{ name }` → 200 → zaktualizować w stanie
- DELETE `/categories/:id` → 204 → usunąć ze stanu
- Obsłużyć kody błędów: 400, 409, 404, 500

## 8. Interakcje użytkownika
1. Wejście na `/categories` → spinner → lista lub empty state
2. Klik `Dodaj kategorię` → otwarcie `CategoryFormModal`
3. Wypełnienie pola → walidacja inline
4. Klik `Zapisz` → spinner → zamknięcie modalu → aktualizacja listy
5. Klik `Edytuj` przy elemencie → wypełniony formularz → edycja analogicznie
6. Klik `Usuń` → otwarcie `ConfirmDialog` → potwierdzenie → usunięcie

## 9. Warunki i walidacja
- Długość nazwy ≤30 → blokada przy wpisie i komunikat inline
- Unikalność nazwy → porównanie z lokalnym stanem i/lub obsługa 409
- Defaultowe kategorie: przy usuwaniu zablokować przycisk `Usuń`

## 10. Obsługa błędów
- Błędy GET: `ErrorDialog` z komunikatem i retry
- Błędy POST/PUT: komunikat inline (400) lub dialog (409, 500)
- Błędy DELETE: dialog z komunikatem (400, 404, 500)

## 11. Kroki implementacji
1. Utworzyć endpoint routingu w Flask: `/templates/categories.html` i JS `/static/js/categories.js`.
2. Przygotować template Jinja2 `categories.html` z rootem komponentu
3. Napisać hooki JS `useCategories()` i `useModal()`
4. Zaimplementować `CategoriesPage` w JS inicjalizujący stan i renderujący UI
5. Stworzyć podkomponenty `LoadingSpinner`, `ErrorDialog`, `EmptyState`, `CategoriesList`, `CategoryFormModal`, `ConfirmDialog`
6. Dodać style Bootstrap i ewentualnie custom CSS
7. Podłączyć eventy i wywołania fetch() według integracji API
8. Przetestować scenariusze: dodawanie, edycja, usuwanie, walidacje, błędy
9. Zapewnić dostępność: focus trap, aria-labels, tab-order
10. Zaimplementować testy e2e dla kluczowych scenariuszy 