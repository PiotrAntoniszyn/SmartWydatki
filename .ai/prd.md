# Dokument wymagań produktu (PRD) - SmartWydatki

## 1. Przegląd produktu
SmartWydatki to webowa aplikacja umożliwiająca użytkownikom rejestrowanie i analizowanie codziennych drobnych wydatków. Dzięki integracji z AI aplikacja automatycznie kategoryzuje wydatki i generuje praktyczne porady, co pozwala lepiej kontrolować finanse.

## 2. Problem użytkownika
Użytkownicy tracą kontrolę nad codziennymi drobnymi wydatkami, które w skali miesiąca sumują się do znaczących kwot. Ręczna analiza wydatków jest pracochłonna i podatna na błędy. Brakuje prostego narzędzia, które automatycznie kategoryzuje wydatki i wskazuje obszary do oszczędności.

## 3. Wymagania funkcjonalne
- Uwierzytelnianie e-mail + hasło, zmiana hasła, usunięcie konta z usunięciem wszystkich danych (RODO).
- Onboarding: wybór 3–5 początkowych kategorii generowanych przez AI.
- Dodawanie wydatku w modalach: kwota (max 2 miejsca dziesiętne), opis (<=100 znaków), statyczna lista max 3 sugestii AI (sortowane wg użycia), przycisk `Zapisz`, modale zamykane tylko przyciskiem.
- Edycja i usuwanie wydatków via modal z potwierdzeniem (OK/Anuluj), bez ponownej kategoryzacji przez AI.
- Zarządzanie kategoriami: dodawanie i edycja nazw (unikalność per użytkownik, max 30 znaków), walidacja i komunikaty błędów inline.
- Lista wydatków: paginacja co 20 rekordów, przyciski `poprzednia`/`następna`, sortowanie według daty malejąco, wyszukiwanie po opisie, filtrowanie po dacie i kwocie, widok pusty „lista jest pusta” z CTA `Dodaj wydatek`.
- AI kategoryzacja: integracja z zewnętrznym API (timeout 10 s, 3 retry), loader podczas oczekiwania, komunikat o błędzie i możliwość retry.
- AI porady finansowe: sugerowane komunikaty po dodaniu wydatku lub w widoku listy (np. „wydajesz więcej niż zwykle na kawę”).
- UI responsywne, format dat DD/MM/YYYY (strefa przeglądarki).
- Logi operacji w bazie (id, timestamp, type [info/warning/error], error_code, message).

## 4. Granice produktu
W MVP nie uwzględniamy:
- importu/eksportu danych,
- wykresów i dashboardów,
- integracji z bankami,
- zaawansowanego filtrowania i edycji wielu rekordów naraz,
- powiadomień push / e-mail,
- aplikacji mobilnych,
- łączenia/dzielenia kategorii,
- archiwizacji logów.

## 5. Historyjki użytkowników
- US-001  
  Tytuł: Rejestracja konta  
  Opis: Użytkownik rejestruje nowe konto podając e-mail i hasło.  
  Kryteria akceptacji:  
    - formularz posiada pola `E-mail` i `Hasło` (min 8 znaków)  
    - po podaniu prawidłowych danych konto zostaje utworzone, a użytkownik trafia do ekranów onboarding  
    - przy próbie rejestracji z istniejącym e-mailem wyświetla się komunikat „E-mail jest już używany” inline  

- US-002  
  Tytuł: Logowanie  
  Opis: Użytkownik loguje się do aplikacji za pomocą e-maila i hasła.  
  Kryteria akceptacji:  
    - formularz logowania posiada pola `E-mail` i `Hasło`  
    - przy podaniu poprawnych danych użytkownik zostaje przekierowany do dashboardu  
    - przy niepoprawnych danych wyświetlany jest komunikat „Nieprawidłowy e-mail lub hasło”  

- US-003  
  Tytuł: Zmiana hasła  
  Opis: Zalogowany użytkownik zmienia hasło w ustawieniach konta.  
  Kryteria akceptacji:  
    - formularz zmiany hasła ma pola `Obecne hasło`, `Nowe hasło`, `Potwierdź nowe hasło`  
    - nowe hasło musi mieć min 8 znaków i odpowiadać obu polom  
    - po pomyślnej zmianie wyświetla się komunikat „Hasło zostało zmienione”  

- US-004  
  Tytuł: Usunięcie konta  
  Opis: Użytkownik usuwa konto wraz ze wszystkimi danymi (wydatkami i kategoriami).  
  Kryteria akceptacji:  
    - proces wymaga potwierdzenia (przycisk `Usuń konto` i `Anuluj`)  
    - po usunięciu konta wszystkie dane użytkownika są usuwane z bazy  
    - użytkownik zostaje wylogowany i przekierowany do strony logowania  

- US-005  
  Tytuł: Onboarding – wybór kategorii  
  Opis: Po rejestracji AI proponuje 3–5 początkowych kategorii, a użytkownik wybiera te, których chce używać.  
  Kryteria akceptacji:  
    - lista propozycji zawiera 3–5 kategorii sugestii AI  
    - użytkownik może wybrać przynajmniej jedną i maksymalnie pięć pozycji  
    - bez wyboru aplikacja nie pozwala przejść dalej  

- US-006  
  Tytuł: Otwieranie modalu dodawania wydatku  
  Opis: Użytkownik klika `Dodaj wydatek` i otwiera się modal z formularzem.  
  Kryteria akceptacji:  
    - modal pojawia się po kliknięciu i focus trafia na pole `Kwota`  
    - nie można zamknąć modalu klikając poza nim ani klawiszem ESC, tylko przyciskiem `Anuluj` lub `Zapisz`  

- US-007  
  Tytuł: Dodanie nowego wydatku  
  Opis: Użytkownik wprowadza kwotę i opcjonalny opis, a następnie zapisuje wydatki.  
  Kryteria akceptacji:  
    - pola `Kwota` i `Opis` walidują odpowiednio: max 2 miejsca dziesiętne, opis <=100 znaków  
    - przy błędnych danych wyświetlany jest komunikat inline pod polem  
    - po kliknięciu `Zapisz` dane trafiają do bazy i modal się zamyka  

- US-008  
  Tytuł: Wyświetlanie sugestii kategorii AI  
  Opis: Po wprowadzeniu opisu i kwoty wyświetlane są statyczne sugestie AI (max 3) sortowane wg użycia.  
  Kryteria akceptacji:  
    - lista sugestii zawiera maksymalnie 3 elementy  
    - sugestie są statyczne (brak typeahead) i sortowane wg częstości użycia  
    - każda sugestia ma nazwę kategorii do wyboru  

- US-009  
  Tytuł: Wybór sugestii AI i zapis wydatku  
  Opis: Użytkownik wybiera jedną z sugestii i zapisuje wydatek.  
  Kryteria akceptacji:  
    - wybór sugestii jest obowiązkowy przed zapisaniem  
    - po wyborze kategorii i kliknięciu `Zapisz` wydatek zostaje zapisany z przypisaną kategorią  

- US-010  
  Tytuł: Loader podczas kategoryzacji AI  
  Opis: System pokazuje loader podczas oczekiwania na odpowiedź AI, jeśli przekracza 200 ms.  
  Kryteria akceptacji:  
    - jeśli odpowiedź AI trwa >200 ms, widoczny jest loader w modal  
    - loader znika po otrzymaniu wyników lub błędzie  

- US-011  
  Tytuł: Obsługa błędu AI i retry  
  Opis: W razie niepowodzenia zapytania AI użytkownik widzi komunikat z opcją retry.  
  Kryteria akceptacji:  
    - przy błędzie wyświetla się komunikat „Błąd kategoryzacji, spróbuj ponownie”  
    - kliknięcie `Retry` ponawia zapytanie do 3 razy z 10 s timeout  

- US-012  
  Tytuł: Edycja wydatku  
  Opis: Użytkownik edytuje istniejący wydatek w modalnym formularzu.  
  Kryteria akceptacji:  
    - modal zawiera wstępnie wypełnione pola `Kwota`, `Opis`, `Kategoria`  
    - pola walidują jak przy dodawaniu  
    - po zapisaniu wartości są aktualizowane w bazie, bez ponownej kategoryzacji AI  

- US-013  
  Tytuł: Usunięcie wydatku  
  Opis: Użytkownik usuwa wydatek przez modal z potwierdzeniem.  
  Kryteria akceptacji:  
    - modal potwierdzający zawiera przyciski `OK`/`Anuluj`  
    - po potwierdzeniu wydatek jest trwale usuwany i lista się odświeża  

- US-014  
  Tytuł: Otwieranie modalu zarządzania kategoriami  
  Opis: Użytkownik otwiera modal do tworzenia/edycji kategorii.  
  Kryteria akceptacji:  
    - modal otwiera się po kliknięciu `Zarządzaj kategoriami`  
    - focus trafia na pole nazwy kategorii  

- US-015  
  Tytuł: Dodanie nowej kategorii  
  Opis: Użytkownik dodaje nową kategorię wpisując unikalną nazwę (<=30 znaków).  
  Kryteria akceptacji:  
    - pole nazwy waliduje max 30 znaków i unikalność per użytkownik  
    - komunikaty błędów wyświetlane inline  
    - po zapisie nowa kategoria pojawia się na liście  

- US-016  
  Tytuł: Edycja istniejącej kategorii  
  Opis: Użytkownik zmienia nazwę istniejącej kategorii.  
  Kryteria akceptacji:  
    - walidacja jak przy dodawaniu  
    - po zapisie nazwa jest aktualizowana w bazie i lista się odświeża  

- US-017  
  Tytuł: Walidacja nazwy kategorii  
  Opis: System waliduje unikalność i długość nazwy kategorii.  
  Kryteria akceptacji:  
    - przy próbie użycia duplikatu lub >30 znaków wyświetlany jest komunikat błędu inline  

- US-018  
  Tytuł: Przeglądanie listy wydatków z paginacją  
  Opis: Użytkownik przegląda wydatki 20 na stronę, korzystając z przycisków prev/next.  
  Kryteria akceptacji:  
    - lista wyświetla maksymalnie 20 rekordów  
    - przyciski `poprzednia`/`następna` przełączają strony  

- US-019  
  Tytuł: Wyszukiwanie wydatków po opisie  
  Opis: Użytkownik wyszukuje wydatki wpisując frazę w polu wyszukiwania.  
  Kryteria akceptacji:  
    - wyszukiwarka filtruje rekordy zawierające wpisaną frazę w opisie  
    - wyszukiwanie jest case-insensitive  

- US-020  
  Tytuł: Filtrowanie wydatków po dacie  
  Opis: Użytkownik filtruje listę wydatków podając zakres dat.  
  Kryteria akceptacji:  
    - można wybrać datę początkową i końcową  
    - lista pokazuje tylko wydatki z zadanego zakresu  

- US-021  
  Tytuł: Filtrowanie wydatków po kwocie  
  Opis: Użytkownik filtruje listę wydatków podając zakres kwot.  
  Kryteria akceptacji:  
    - można podać minimalną i maksymalną kwotę  
    - lista pokazuje tylko wydatki z zadanego zakresu  

- US-022  
  Tytuł: Widok pustej listy wydatków  
  Opis: Nowy lub nieaktywny użytkownik widzi komunikat, gdy lista jest pusta.  
  Kryteria akceptacji:  
    - gdy brak wydatków, widoczny jest komunikat „lista jest pusta”  
    - przycisk `Dodaj wydatek` jest dostępny i otwiera modal  

- US-023  
  Tytuł: Wyświetlanie podsumowania tygodniowego  
  Opis: Użytkownik widzi w widoku listy sumę wydatków i liczbę transakcji z ostatniego tygodnia.  
  Kryteria akceptacji:  
    - na górze listy jest widoczny tygodniowy podsumowujący pasek  
    - pokazana jest suma wydatków oraz liczba transakcji  

- US-024  
  Tytuł: Wyświetlanie porad AI w widoku listy  
  Opis: AI podpowiada użytkownikowi wskazówki finansowe w widoku listy wydatków.  
  Kryteria akceptacji:  
    - AI generuje maksymalnie 3 porady na sesję  
    - porady są wyświetlane w dobrze widocznym miejscu nad/obok listy  

- US-025  
  Tytuł: Bezpieczny dostęp  
  Opis: Tylko uwierzytelnieni użytkownicy mogą przeglądać dane.  
  Kryteria akceptacji:  
    - próba wejścia na stronę bez logowania przekierowuje na ekran logowania  
    - po wylogowaniu dostęp do zasobów jest zablokowany  

- US-026  
  Tytuł: Walidacja kwoty wydatku  
  Opis: System waliduje poprawność formatu kwoty.  
  Kryteria akceptacji:  
    - akceptowane są liczby z maksymalnie 2 miejscami po przecinku  
    - przy wpisaniu formatu niezgodnego wyświetlany jest komunikat inline  

- US-027  
  Tytuł: Walidacja długości opisu wydatku  
  Opis: System waliduje maksymalną długość opisu.  
  Kryteria akceptacji:  
    - opis nie może przekraczać 100 znaków  
    - przy przekroczeniu limitu wyświetlany jest komunikat inline  

- US-028  
  Tytuł: Zamykanie modali tylko przyciskami  
  Opis: Modal można zamknąć tylko przyciskiem, nie przez kliknięcie poza modal ani klawiszem ESC.  
  Kryteria akceptacji:  
    - kliknięcie poza modalem lub naciśnięcie ESC nie zamyka go  

- US-029  
  Tytuł: Domyślne sortowanie wydatków  
  Opis: Listę wydatków domyślnie sortuje się według daty malejąco.  
  Kryteria akceptacji:  
    - po wejściu na stronę lista jest posortowana od najnowszych do najstarszych  

- US-030  
  Tytuł: Rejestrowanie operacji w logach  
  Opis: System zapisuje zdarzenia w tabeli logów w bazie.  
  Kryteria akceptacji:  
    - każde dodanie, edycja, usunięcie wydatku zapisuje wpis w tabeli logów z wymaganymi polami  

## 6. Metryki sukcesu
- AI kategoryzuje poprawnie co najmniej 75% wydatków.  
- Użytkownik akceptuje co najmniej 75% sugerowanych kategorii.  
- Czas od kliknięcia `Zapisz` do wyświetlenia propozycji AI jest krótszy niż 30 sekund.  
- Monitorowane metryki: średni czas sesji (od otwarcia modalu do zatwierdzenia), wskaźnik akceptacji AI, liczba dodanych wydatków, liczba wyszukań, liczba paginacji.