# Dokumentacja widoku Dashboard

## Opis ogólny
Widok Dashboard dostarcza użytkownikowi szybki przegląd stanu finansów w formie tygodniowego podsumowania wydatków oraz spersonalizowanych porad AI. Jest to główny ekran aplikacji, który zapewnia użytkownikowi wartościowe informacje na pierwszy rzut oka.

## Struktura komponentów

### 1. WeeklySummaryCard
Komponent wyświetlający podsumowanie wydatków z bieżącego tygodnia:
- Suma kwot transakcji
- Liczba przeprowadzonych transakcji

### 2. AiTipsPanel
Panel pokazujący maksymalnie trzy spersonalizowane porady AI dotyczące zarządzania finansami, generowane na podstawie historii transakcji użytkownika.

## Przepływ danych

1. **Inicjalizacja**:
   - Po załadowaniu strony asynchronicznie pobierane są dane z dwóch endpointów API
   - W trakcie ładowania pokazywane są spinnery
   - Jeśli ładowanie trwa dłużej niż 200ms, spinner staje się widoczny

2. **Zapytania API**:
   - `/expenses/summary?period=weekly` - tygodniowe podsumowanie
   - `/ai/tips?limit=3` - porady AI (maksymalnie 3)

3. **Obsługa błędów**:
   - W przypadku problemów z API wyświetlany jest komunikat błędu
   - Użytkownik ma możliwość ponowienia zapytania
   - Błędy są logowane na serwerze

## Rozszerzanie funkcjonalności

### Dodawanie nowych okresów podsumowania
Obecnie obsługiwane jest tylko podsumowanie tygodniowe. Aby dodać inny okres:

1. Rozszerz endpoint `/expenses/summary` o obsługę nowego parametru `period`
2. Dodaj nową logikę w kontrolerze dla obliczenia dat odpowiadających nowemu okresowi
3. Zmodyfikuj UI o możliwość przełączania między okresami

### Modyfikacja panelu porad AI
Aby zmienić sposób generowania lub prezentacji porad AI:

1. Zmodyfikuj endpoint `/ai/tips` do integracji z rzeczywistym serwisem AI
2. Dostosuj model danych jeśli potrzebne są dodatkowe pola
3. Zaktualizuj logikę renderowania w JavaScript

## Dostępność (A11y)
Widok jest zoptymalizowany pod kątem dostępności:

- Wykorzystuje atrybuty `aria-live` do notyfikowania o zmianach zawartości
- Statusy ładowania są komunikowane przez `aria-busy`
- Wszystkie komponenty posiadają odpowiednie oznaczenia ARIA
- Fokusowalne nagłówki dla nawigacji klawiaturą
- Przyciski posiadają opisowe etykiety

## Testowanie
Do testów widoku wykorzystujemy Cypress. Testy obejmują:

1. **Renderowanie komponentów**:
   - Poprawne wyświetlanie podczas ładowania
   - Poprawne wyświetlanie po załadowaniu danych
   - Pokazywanie odpowiednich komunikatów dla pustych danych

2. **Obsługa błędów**:
   - Wyświetlanie komunikatów błędów
   - Funkcjonalność przycisków "Spróbuj ponownie"

3. **Integracja z API**:
   - Poprawne przetwarzanie odpowiedzi z endpointów
   - Limity danych (max 3 porady)

4. **Dostępność**:
   - Weryfikacja atrybutów ARIA
   - Testowanie fokusowania elementów

## FAQ dla developerów

**P: Jak dodać nowy typ porad AI?**
O: Zmodyfikuj model danych `AiTip` w schemacie, zaktualizuj logikę generowania w `/ai/tips` oraz dostosuj rendering w `dashboard.js`.

**P: Jak zmienić format wyświetlania kwot?**
O: Zmodyfikuj funkcję `renderSummary()` w `dashboard.js`, zmieniając ustawienia `toLocaleString()`.

**P: Jak rozszerzyć summary o nowe metryki?**
O: Rozszerz model `ExpenseSummary`, dodaj nowe obliczenia w kontrolerze API i zaktualizuj HTML oraz funkcję `renderSummary()`. 