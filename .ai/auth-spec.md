# Specyfikacja modułu autentykacji (Rejestracja, Logowanie, Zarządzanie kontem)

Poniższa dokumentacja opisuje architekturę frontendową i backendową oraz integrację z systemem Supabase Auth, zgodnie z wymaganiami PRD i stosowanym stackiem technologicznym.

---

## 1. ARCHITEKTURA INTERFEJSU UŻYTKOWNIKA

### 1.1 Layouty i nawigacja

1. Layout non-auth (`BaseNonAuth`)
   - Nagłówek: logo, minimalna nawigacja (linki: Logowanie, Rejestracja)
   - Główna sekcja: renderowanie treści stron auth
   - Stopka: prawa autorskie

2. Layout auth (`BaseAuth`)
   - Nagłówek: logo, przycisk Wyloguj w prawym górnym rogu, menu użytkownika
   - Pasek boczny (opcjonalny): linki do głównych funkcji po zalogowaniu
   - Stopka: pozostałe linki

### 1.2 Strony i komponenty

#### Strony:
- `/register` – formularz rejestracji (pola: E-mail, Hasło, Potwierdź Hasło)
- `/login` – formularz logowania (pola: E-mail, Hasło)
- `/onboarding` - ekran wyboru początkowych kategorii po rejestracji
- `/settings/account` – strona ustawień konta z formularzem zmiany hasła (Obecne Hasło, Nowe Hasło, Potwierdź Nowe Hasło) oraz przyciskiem usunięcia konta

#### Komponenty formularzy (Jinja2 + Bootstrap/Tailwind + vanilla JS):
- `FormInput` – uniwersalny input z etykietą, placeholderem, obsługą `value` i `errorText`
- `PasswordInput` – rozszerzenie `FormInput` z przełącznikiem widoczności hasła
- `ButtonPrimary` / `ButtonSecondary` – spójny styl
- `ValidationMessage` – wyświetlanie komunikatów błędów inline pod polem
- `FlashMessage` – globalne komunikaty sukcesu/błędu

#### Rozdzielenie odpowiedzialności:
- Strony (Flask + Jinja2 templates) renderują strukturę i ładowanie komponentów
- Komponenty JS odpowiadają za:
  - walidację klienta (format email, długość hasła, porównanie haseł)
  - obsługę `fetch` do endpointów API
  - obsługę loadera i blokadzie przycisku wysyłki
  - wyświetlanie komunikatów błędów zwróconych przez backend
  - przekierowania po sukcesie (np. do `/login` albo dashboardu)

### 1.3 Walidacja i komunikaty błędów

1. Rejestracja:
   - Email: regex RFC 5322, komunikat „Nieprawidłowy format e-mail”
   - Hasło: min. 8 znaków, komunikat „Hasło musi mieć co najmniej 8 znaków”
   - Powtórz hasło: musi odpowiadać polu Hasło, komunikat „Hasła nie są identyczne”
   - Duplikat email: komunikat zwrócony z API „E-mail jest już używany”

2. Logowanie:
   - Email/Hasło: jeśli niepasujące do konta, komunikat „Nieprawidłowy e-mail lub hasło”

3. Zmiana hasła:
   - Obecne hasło: wymagane, komunikat „Podaj obecne hasło” przy braku.
   - Nowe hasło: min. 8 znaków, komunikat „Hasło musi mieć co najmniej 8 znaków”.
   - Potwierdzenie nowego hasła: musi odpowiadać polu Nowe hasło, komunikat „Hasła nie są identyczne”.

4. Usunięcie konta:
   - Potwierdzenie działania: modal z przyciskami `Usuń konto` i `Anuluj`.

### 1.4 Główne scenariusze użytkownika

- Otwieranie `/register` → wypełnienie formularza → walidacja klienta → wysłanie → obsługa błędów API → przekierowanie na `/onboarding`
- Wybór kategorii w `/onboarding` → zapisanie wybranych kategorii → przekierowanie do dashboardu
- Otwieranie `/login` → wysłanie → ustawienie ciasteczka sesji → przekierowanie do dashboardu
- Zmiana hasła w `/settings/account` → wypełnienie pól Obecne hasło, Nowe hasło, Potwierdź nowe hasło → walidacja klienta i API → komunikat „Hasło zostało zmienione"
- Usunięcie konta w `/settings/account` → kliknięcie `Usuń konto` → modal potwierdzenia → po potwierdzeniu usunięcie danych i przekierowanie do `/login`

---

## 2. LOGIKA BACKENDOWA

### 2.1 Struktura endpointów API

| Metoda | Ścieżka                        | Opis                                     |
|--------|--------------------------------|------------------------------------------|
| POST   | `/api/auth/register`           | Rejestracja użytkownika                  |
| POST   | `/api/auth/login`              | Logowanie                                |
| POST   | `/api/auth/logout`             | Wylogowanie                              |
| POST   | `/api/auth/password/change`    | Zmiana hasła (wymaga obecnego hasła)     |
| DELETE | `/api/auth/account`            | Usunięcie konta i wszystkich danych (RODO)|
| GET    | `/api/categories/suggestions`  | Pobranie sugestii kategorii dla onboardingu |
| POST   | `/api/categories/initial`      | Zapisanie wybranych początkowych kategorii |

#### Modele DTO i dane wejściowe

- `AuthRegisterInput { email: string, password: string, passwordConfirm: string }`
- `AuthLoginInput { email: string, password: string }`
- `AuthChangePasswordInput { currentPassword: string, newPassword: string, passwordConfirm: string }`
- `InitialCategoriesInput { categoryIds: string[] }`

#### Odpowiedzi
- Sukces: `{ status: 'ok', message?: string }`
- Błąd walidacji: HTTP 400 + `{ field: 'email'|'password'|'token', error: string }`
- Błąd autoryzacji: HTTP 401 + `{ error: string }`
- Błąd serwera: HTTP 500 + `{ error: string }`

### 2.2 Walidacja danych wejściowych

- Użycie dekoratorów lub Flask-Inputs/Cerberus:
  - sprawdzanie typów, długości, formatów
  - centralne łapanie błędów walidacji i zwrócenie ujednoliconego JSON

### 2.3 Obsługa wyjątków

- Globalny handler `@app.errorhandler(Exception)`:
  - Specjalne typy błędów (ValidationError, SupabaseError)
  - Domyślny 500 dla nieznanych wyjątków

- Mapowanie błędów Supabase (np. `AuthApiError`) na odpowiednie kody HTTP i komunikaty

### 2.4 Renderowanie server-side (Jinja2 + Astro)

1. Szablony Jinja2:
   - `register.html`, `login.html` dziedziczące po `BaseNonAuth`
   - `settings_account.html` dziedziczący po `BaseAuth`
   - Bloki `content` z formularzami i `flash` na komunikaty

2. Aktualizacja `astro.config.mjs` (SSR):
```js
import { defineConfig } from 'astro/config';
import node from '@astrojs/node';

export default defineConfig({
  output: 'server',
  adapter: node(),
  ssr: {
    entrypoints: [
      '/register',
      '/login'
    ]
  }
});
```
- Dzięki temu strony auth będą serwerowane przez Flask + Astro SSR bez przerywania obecnej architektury.

---

## 3. SYSTEM AUTENTYKACJI

### 3.1 Integracja z Supabase Auth

1. Konfiguracja klienta (w `app/__init__.py` lub `config.py`):
   - `SUPABASE_URL`, `SUPABASE_KEY` jako zmienne środowiskowe
   - Inicjalizacja `supabase = create_client(url, key)`

2. Implementacja w kontrolerach:
   - Rejestracja: `supabase.auth.sign_up({ email, password })` → przekierowanie do onboardingu
   - Logowanie: `supabase.auth.sign_in({ email, password })` → ustawienie secure HTTP-only cookie z tokenem sesji
   - Wylogowanie: `supabase.auth.sign_out()` + usunięcie cookie
   - Zmiana hasła: `supabase.auth.update({ password: newPassword })` (autoryzacja na podstawie sesji), weryfikacja obecnego hasła przed wysłaniem
   - Usunięcie konta: `supabase.auth.api.delete_user(user_id)` wraz z kaskadowym usunięciem danych

3. Proces onboardingu:
   - Po rejestracji (`/api/auth/register`) użytkownik jest automatycznie przekierowywany na stronę `/onboarding`
   - Na stronie onboardingu system pobiera z AI 3-5 propozycji kategorii (`/api/categories/suggestions`)
   - Użytkownik musi wybrać przynajmniej jedną kategorię przed przejściem dalej
   - Po zapisaniu wybranych kategorii (`/api/categories/initial`), użytkownik trafia do głównego dashboardu

4. Zabezpieczenia i ograniczenia:
   - Nie implementujemy logowania przez zewnętrzne serwisy (Google, GitHub, itp.) zgodnie z PRD
   - Wszystkie endpointy aplikacji są chronione middleware sprawdzającym obecność i ważność tokenu sesji
   - Strony aplikacji poza `/login` i `/register` są niedostępne dla niezalogowanych użytkowników

### 3.2 Bezpieczeństwo i RODO

- CSRF: tokeny w formularzach (Flask-WTF)
- HTTPS: wymuszenie w prod (Flask-Talisman)
- Rate limiting: Flask-Limiter na endpointach auth
- Logowanie operacji: tabela `logs` w Supabase (wbudowany klient SQL)
- RODO: na żądanie usuwamy konto i dane (usuwanie usera przez `supabase.auth.api.delete_user(user_id)` i cascade drop danych)

---

*W powyższej specyfikacji uwzględniono istniejące wymagania MVP, zgodność z frontendowym stackiem (Flask+Jinja2, Bootstrap/Tailwind, vanilla JS) oraz centralizację logiki autoryzacji poprzez Supabase Auth.* 