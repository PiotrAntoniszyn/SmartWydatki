# Plan implementacji widoku Dashboard

## 1. Przegląd
Widok Dashboard ma za zadanie dostarczyć użytkownikowi:  
- tygodniowe podsumowanie wydatków (suma kwot i liczba transakcji),  
- maksymalnie trzy spersonalizowane porady finansowe generowane przez AI.  
Jego celem jest szybkie przedstawienie kluczowych metryk i rekomendacji, aby wspierać świadome zarządzanie finansami.

## 2. Routing widoku
- Ścieżka w aplikacji: `/dashboard`  
- Flask route:  
  ```python
  @app.route('/dashboard')
  @login_required
  def dashboard():
      return render_template('dashboard.html')
  ```
- Link w nawigacji: element menu prowadzący do `/dashboard`.

## 3. Struktura komponentów
- **dashboard.html** (główny szablon Jinja2)  
  ├─ Blok: **WeeklySummaryCard** (`<div id="weekly-summary" aria-live="polite">`)  
  ├─ Blok: **AiTipsPanel** (`<div id="ai-tips-panel" aria-live="polite">`)  
  ├─ Komponenty wspólne: **LoadingSpinner**, **ErrorAlert**  
  └─ Import skryptu: `static/js/dashboard.js`

## 4. Szczegóły komponentów

### WeeklySummaryCard
- Opis: wyświetla sumę wydatków i liczbę transakcji z ostatniego tygodnia.
- Główne elementy HTML:
  ```html
  <div id="weekly-summary" class="card p-3" aria-live="polite">
    <div class="spinner-border" id="summary-spinner" role="status"></div>
    <div id="summary-content" class="d-none">
      <p>Łączna kwota: <span id="total-amount"></span> PLN</p>
      <p>Liczba transakcji: <span id="transaction-count"></span></p>
    </div>
    <div id="summary-error" class="alert alert-danger d-none">
      Błąd ładowania podsumowania. <button id="summary-retry" class="btn btn-link">Retry</button>
    </div>
  </div>
  ```
- Obsługiwane zdarzenia:
  - Automatyczne wywołanie `fetchWeeklySummary()` po załadowaniu strony.  
  - Kliknięcie w przycisk `#summary-retry` wywołuje ponownie fetch.
- Walidacja: brak danych traktowane jako 0 i "0 transakcji".
- Typy:
  ```js
  /** @typedef {{ total_amount: number, transaction_count: number }} ExpenseSummary */
  ```
- Propsy: brak (dane dynamicznie pobierane w JS).

### AiTipsPanel
- Opis: prezentuje do trzech porad AI nad listą wydatków.
- Główne elementy HTML:
  ```html
  <div id="ai-tips-panel" class="card p-3 mt-4" aria-live="polite">
    <div class="spinner-border" id="tips-spinner" role="status"></div>
    <ul id="tips-list" class="list-group d-none"></ul>
    <div id="tips-error" class="alert alert-danger d-none">
      Błąd ładowania porad AI. <button id="tips-retry" class="btn btn-link">Retry</button>
    </div>
  </div>
  ```
- Obsługiwane zdarzenia:
  - Automatyczne wywołanie `fetchAiTips()` po załadowaniu strony.
  - Kliknięcie `#tips-retry` wywołuje ponownie fetch.
- Walidacja: maksymalnie 3 elementy w liście.
- Typy:
  ```js
  /** @typedef {{ message: string }} AiTip */
  ```
- Propsy: brak.

### LoadingSpinner i ErrorAlert
- **LoadingSpinner**: wykorzystanie klasy Bootstrap `spinner-border`.  
- **ErrorAlert**: element Bootstrap `.alert.alert-danger` z przyciskiem retry.

## 5. Typy
- ExpenseSummary:
  - `total_amount: number`  
  - `transaction_count: number`
- AiTip:
  - `message: string`

## 6. Zarządzanie stanem
- Vanilla JS w `static/js/dashboard.js`:
  - Flagi: `loadingSummary`, `loadingTips`, `errorSummary`, `errorTips`  
  - Dane: `summaryData`, `tipsData`  
  - Funkcje: `fetchWeeklySummary()`, `fetchAiTips()`, `renderSummary()`, `renderTips()`, `showError()`, `showSpinner()`.

## 7. Integracja API
- **GET /expenses/summary?period=weekly**
  - Response: `ExpenseSummary`  
- **GET /ai/tips?limit=3**
  - Response: `AiTip[]`
- Implementacja fetch w JS:
  ```js
  fetch('/expenses/summary?period=weekly')
  fetch('/ai/tips?limit=3')
  ```
- Timeout >200 ms → pokazanie spinnera (setTimeout).

## 8. Interakcje użytkownika
- Autonomiczne ładowanie danych po otwarciu Dashboard.
- Kliknięcie "Retry" przy błędzie ponawia żądanie.
- Dynamika aktualizacji: aria-live zapewnia uaktualnienie asystujące dostępność.

## 9. Warunki i walidacja
- `limit` w parametrze AI nigdy >3 (frontend zawsze `?limit=3`).
- `period=weekly` narzucone.
- Jeśli `transaction_count === 0`, można wyświetlić komunikat "Brak danych za ten tydzień".

## 10. Obsługa błędów
- Sieć/HTTP (status ≠ 200): wyświetlenie `.alert.alert-danger` z komunikatem i Retry.
- Brak wyników: pusta lista lub komunikat "Brak porad do wyświetlenia".

## 11. Kroki implementacji
1. Dodać trasę `/dashboard` w Flask i w menu nawigacji.  
2. Utworzyć szablon `dashboard.html` w `templates/`.  
3. Zaimplementować strukturę HTML dla sekcji podsumowania i porad AI.  
4. Dodać plik `static/js/dashboard.js` z logiką fetch + render.  
5. Podłączyć skrypt w `dashboard.html`.  
6. Przetestować ładowanie, loader, retry, aria-live.  
7. Przegląd kodu i uwzględnienie uwag z QA. 