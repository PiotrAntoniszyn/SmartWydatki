# OpenRouter Service – Plan wdrożenia

## 1. Opis usługi
OpenRouter Service (``openrouter_service``) jest lekką, bezstanową warstwą pomiędzy Twoją aplikacją Flask a API https://openrouter.ai.  Odpowiada za:

* budowanie i walidację zapytań *chat completions* (system/user/assistant),
* ustawianie parametrów modelu oraz ``response_format``,
* ponawianie żądań z ekspotencjalnym *back-off*,
* podstawową agregację metryk i logów w celu monitoringu,
* bezpieczne zarządzanie kluczem API (ENV + Secret Scanning),
* obsługę błędów sieciowych, limitów oraz walidację odpowiedzi.

Architektura jest zgodna z udostępnionym stackiem (Python 3.11 + Flask, Supabase, GitHub Actions, Docker/DigitalOcean).

---

## 2. Opis konstruktora
```python
class OpenRouterService:
    def __init__(
        self,
        api_key: str,
        model_name: str = "openrouter/azure/gpt-4o",
        *,
        base_url: str = "https://openrouter.ai/api/v1",
        timeout: float = 30.0,
        max_retries: int = 3,
        backoff_factor: float = 2.0,
        default_system_prompt: str | None = None,
        default_response_format: dict | None = None,
        http_client: HTTPClientProtocol | None = None,
    ):  ...
```
Parametry konstruktora:
1. ``api_key`` – klucz OpenRouter z panelu; przekazywany wyłącznie przez zmienną środowiskową ``OPENROUTER_API_KEY``.
2. ``model_name`` – domyślny model; można nadpisać per request.
3. ``timeout`` – limit czasowy na połączenie + odczyt.
4. ``max_retries`` & ``backoff_factor`` – sterują automatycznym ponawianiem.
5. ``default_system_prompt`` & ``default_response_format`` – wartości globalne, które mogą być modyfikowane przy konkretnym wywołaniu.
6. ``http_client`` – implementacja ``httpx.AsyncClient`` lub zgodny adapter (ułatwia testy jednostkowe).

---

## 3. Publiczne metody i pola
| Metoda / Pole | Sygnatura | Cel |
|---------------|-----------|------|
| ``chat_completion`` | ``async def chat_completion(self, messages: list[dict[str, str]], *, model_params: dict[str, Any] | None = None, response_format: dict | None = None) -> dict`` | Główne wejście dla UI/API. Buduje payload, wysyła do OpenRouter oraz zwraca zparsowaną odpowiedź. |
| ``generate_completion`` | ``async def generate_completion(self, prompt: str, **kwargs) -> str`` | Skrót dla jednokrotnego ``user`` promptu (tworzy listę ``messages``). |
| ``health_check`` | ``def health_check(self) -> bool`` | Krótki ping do ``/models``; używany w liveness probe Dockera. |
| ``model_name`` | ``str`` | Bieżący model (mutowalny). |
| ``base_url`` | ``str`` | Bazowy URL API. |

---

## 4. Prywatne metody i pola
* ``_build_payload(messages, model_params, response_format)`` – składa końcowy JSON.
* ``_post_with_retry(endpoint, payload)`` – wywołuje ``http_client`` z polityką ponawiania.
* ``_validate_response(resp_json, response_format)`` – sprawdza zgodność z ``json_schema`` jeśli podany *strict mode*.
* ``_handle_rate_limit(retry_after)`` – usypia korutynę / prosi klienta UI o ponowną próbę.
* ``_log_request`` & ``_log_error`` – integracja z loggerem standardowym lub OpenTelemetry.
* ``_mask_secrets`` – usuwa klucze API z logów.

---

## 5. Obsługa błędów
1. **Timeout (Connect / Read)**  
   * Wykrywane przez ``httpx.TimeoutException``.  
   * Rozwiązanie: ponów do ``max_retries`` z back-off; komunikat do UI o przekroczeniu czasu.
2. **HTTP 429 – Rate Limit**  
   * Odczytaj nagłówek ``Retry-After`` i uśp klienta; po trzeciej nieudanej próbie zwróć błąd ``503 Service Unavailable`` do Flask.  
3. **HTTP 4xx (np. 401, 403)**  
   * Propaguj status i przyjazny komunikat; zarejestruj w systemie alertów.
4. **HTTP 5xx**  
   * Ponów żądanie (bo błąd serwera) – zgodnie ze strategiami  exponential back-off.
5. **Błąd walidacji ``response_format``**  
   * Podnieś ``OpenRouterSchemaError``; w UI komunikat "Model zwrócił niezgodny JSON – spróbuj ponownie/zgłoś błąd".
6. **Brak klucza API**  
   * Podczas konstrukcji instancji – rzuć ``OpenRouterConfigError`` zanim wystartuje aplikacja.

---

## 6. Kwestie bezpieczeństwa
* Przechowuj ``OPENROUTER_API_KEY`` w Secretach GitHub/DigitalOcean; nigdy w repo.
* Wymuś TLS 1.2+; ``httpx`` ma włączone domyślnie.
* Filtruj prompty użytkownika pod kątem wstrzyknięć prompt-hacking (np. regex + RAG).
* Loguj wyłącznie skrócone prompty (<512 znaków) oraz skrócone odpowiedzi.
* Zabezpiecz endpoint Flask (rate limiting, CSRF token dla żądań POST z przeglądarki).

---

## 7. Plan wdrożenia krok po kroku

### 7.1 Przygotowanie repozytorium
1. ``python -m venv .venv && source .venv/bin/activate``  
2. ``pip install httpx[http2] flask python-dotenv pydantic backoff``  
3. Dodaj ``requirements.txt`` i ``pip freeze > requirements.txt``.
4. Utwórz moduł ``/app/openrouter_service.py`` i zaimplementuj klasę wg powyższej specyfikacji.
5. Dodaj testy ``pytest`` z ``httpx.MockTransport``.

### 7.2 Integracja z Flask
```python
from app.openrouter_service import OpenRouterService

service = OpenRouterService(api_key=os.getenv("OPENROUTER_API_KEY"))

@app.route("/api/chat", methods=["POST"])
async def chat_api():
    data = request.get_json(force=True)
    messages = data["messages"]
    params = data.get("params", {})
    resp = await service.chat_completion(messages, model_params=params)
    return jsonify(resp)
```

### 7.3 Przykładowe konfiguracje zapytania
1. **Komunikat systemowy**  
   ```python
   system_prompt = "Jesteś pomocnym asystentem odpowiadającym po polsku."
   messages = [{"role": "system", "content": system_prompt},
               {"role": "user", "content": "Wymień stacje na linii M2"}]
   await service.chat_completion(messages)
   ```
2. **Komunikat użytkownika** – jak wyżej, ``role='user'``.
3. **Ustrukturyzowana odpowiedź (``response_format``)**  
   ```python
   product_schema = {
       "type": "json_schema",
       "json_schema": {
           "name": "product_search",
           "strict": True,
           "schema": {
               "type": "object",
               "properties": {
                   "product_name": {"type": "string"},
                   "max_results": {"type": "integer", "minimum": 1, "maximum": 20}
               },
               "required": ["product_name", "max_results"]
           }
       }
   }
   await service.chat_completion(messages, response_format=product_schema)
   ```
4. **Nazwa modelu**  
   ```python
   await service.chat_completion(messages, model_params={"model": "openrouter/anthropic/claude-3-opus"})
   ```
5. **Parametry modelu**  
   ```python
   await service.chat_completion(
       messages,
       model_params={"temperature": 0.2, "max_tokens": 1024, "top_p": 0.95}
   )
   ```

### 7.4 CI/CD (GitHub Actions)
* Workflow z jobem *lint+test*, budowaniem obrazu Dockera oraz wypchnięciem do DigitalOcean Container Registry.
* Użyj gotowych akcji ``docker/login-action`` i ``docker/build-push-action``.

### 7.5 Docker & DigitalOcean
1. ``Dockerfile`` (slim-python 3.11 + ``pip install -r requirements.txt``).  
2. Ustaw ``CMD gunicorn -k uvicorn.workers.UvicornWorker app.main:app`` (async Flask via Quart lub use stand-alone ASGI layer).  
3. Dodaj ``healthcheck" curl -f http://localhost:8000/health || exit 1"``.
4. Na DigitalOcean uruchom kontener z sekretami (``OPENROUTER_API_KEY``) i autolinkiem do repo.

### 7.6 Monitoring & alerty
* Eksportuj metryki (czas odpowiedzi, liczba retry, kody HTTP) do Prometheus poprzez ``/metrics``.
* Alert na >1% błędów 5xx lub średni czas odpowiedzi >3 s.

---

> Gotowe!  Po zaimplementowaniu powyższych kroków usługa OpenRouter będzie skalowalna, odporna na błędy i łatwa w utrzymaniu w ramach Twojego stacku Flask + Supabase + DigitalOcean. 