/**
 * Dashboard - skrypt obsługujący funkcjonalność widoku głównego dashboardu
 * 
 * Skrypt odpowiada za:
 * 1. Pobieranie danych podsumowania wydatków i porad AI z API
 * 2. Renderowanie danych w odpowiednich komponentach
 * 3. Obsługę stanów ładowania i błędów
 * 4. Zapewnienie dostępności (ARIA attributes)
 * 
 * @author Zespół Finansowy
 * @version 1.0.0
 */

/**
 * @typedef {{ total_amount: number, transaction_count: number }} ExpenseSummary
 * @typedef {{ message: string }} AiTip
 */

// Zmienne stanu
let loadingSummary = false;
let loadingTips = false;
let errorSummary = false;
let errorTips = false;
let summaryData = null;
let tipsData = null;

// Elementy DOM
const summarySpinner = document.getElementById('summary-spinner');
const summaryContent = document.getElementById('summary-content');
const summaryError = document.getElementById('summary-error');
const summaryRetry = document.getElementById('summary-retry');
const totalAmount = document.getElementById('total-amount');
const transactionCount = document.getElementById('transaction-count');

const tipsSpinner = document.getElementById('tips-spinner');
const tipsContent = document.getElementById('tips-content');
const tipsList = document.getElementById('tips-list');
const tipsError = document.getElementById('tips-error');
const tipsRetry = document.getElementById('tips-retry');

/**
 * Funkcje pomocnicze dla zarządzania stanem UI
 * Każda funkcja aktualizuje zarówno klasy CSS jak i atrybuty ARIA
 * dla zapewnienia poprawnej dostępności
 */

/**
 * Pokazuje spinner ładowania dla danego komponentu
 * Ukrywa jednocześnie zawartość i komunikat błędu
 * 
 * @param {string} component - 'summary' lub 'tips'
 */
function showSpinner(component) {
  if (component === 'summary') {
    summarySpinner.classList.remove('d-none');
    summarySpinner.setAttribute('aria-hidden', 'false');
    summaryContent.classList.add('d-none');
    summaryContent.setAttribute('aria-hidden', 'true');
    summaryError.classList.add('d-none');
    summaryError.setAttribute('aria-hidden', 'true');
  } else if (component === 'tips') {
    tipsSpinner.classList.remove('d-none');
    tipsSpinner.setAttribute('aria-hidden', 'false');
    tipsContent.classList.add('d-none');
    tipsContent.setAttribute('aria-hidden', 'true');
    tipsError.classList.add('d-none');
    tipsError.setAttribute('aria-hidden', 'true');
  }
}

/**
 * Pokazuje zawartość dla danego komponentu
 * Ukrywa jednocześnie spinner i komunikat błędu
 * 
 * @param {string} component - 'summary' lub 'tips'
 */
function showContent(component) {
  if (component === 'summary') {
    summarySpinner.classList.add('d-none');
    summarySpinner.setAttribute('aria-hidden', 'true');
    summaryContent.classList.remove('d-none');
    summaryContent.setAttribute('aria-hidden', 'false');
    summaryError.classList.add('d-none');
    summaryError.setAttribute('aria-hidden', 'true');
  } else if (component === 'tips') {
    tipsSpinner.classList.add('d-none');
    tipsSpinner.setAttribute('aria-hidden', 'true');
    tipsContent.classList.remove('d-none');
    tipsContent.setAttribute('aria-hidden', 'false');
    tipsError.classList.add('d-none');
    tipsError.setAttribute('aria-hidden', 'true');
  }
}

/**
 * Pokazuje komunikat błędu dla danego komponentu
 * Ukrywa jednocześnie spinner i zawartość
 * 
 * @param {string} component - 'summary' lub 'tips'
 */
function showError(component) {
  if (component === 'summary') {
    summarySpinner.classList.add('d-none');
    summarySpinner.setAttribute('aria-hidden', 'true');
    summaryContent.classList.add('d-none');
    summaryContent.setAttribute('aria-hidden', 'true');
    summaryError.classList.remove('d-none');
    summaryError.setAttribute('aria-hidden', 'false');
  } else if (component === 'tips') {
    tipsSpinner.classList.add('d-none');
    tipsSpinner.setAttribute('aria-hidden', 'true');
    tipsContent.classList.add('d-none');
    tipsContent.setAttribute('aria-hidden', 'true');
    tipsError.classList.remove('d-none');
    tipsError.setAttribute('aria-hidden', 'false');
  }
}

/**
 * Pobiera dane podsumowania tygodniowego z API
 * Aktualizuje stan ładowania oraz obsługuje błędy
 * 
 * @returns {Promise<void>}
 */
async function fetchWeeklySummary() {
  if (loadingSummary) return;
  
  loadingSummary = true;
  errorSummary = false;
  showSpinner('summary');
  
  // Oznaczenie dla czytników ekranu, że trwa ładowanie
  const weeklyCard = document.getElementById('weekly-summary');
  weeklyCard.setAttribute('aria-busy', 'true');
  
  // Dodajemy timeout dla pokazania spinnera
  // Jeśli ładowanie trwa krócej niż 200ms, spinner może migać
  const spinnerTimeout = setTimeout(() => {
    // Pusty callback - spinner będzie widoczny przez co najmniej 200ms
  }, 200);
  
  try {
    // Wywołanie API dla podsumowania tygodniowego
    const response = await fetch('/expenses/summary?period=weekly');
    
    // Obsługa błędów HTTP
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    /** @type {ExpenseSummary} */
    const data = await response.json();
    summaryData = data;
    renderSummary();
    
  } catch (error) {
    // Logowanie błędu i aktualizacja stanu
    console.error('Error fetching weekly summary:', error);
    errorSummary = true;
    showError('summary');
    weeklyCard.setAttribute('aria-busy', 'false');
  } finally {
    loadingSummary = false;
    clearTimeout(spinnerTimeout);
  }
}

/**
 * Pobiera porady AI z API
 * Aktualizuje stan ładowania oraz obsługuje błędy
 * 
 * @returns {Promise<void>}
 */
async function fetchAiTips() {
  if (loadingTips) return;
  
  loadingTips = true;
  errorTips = false;
  showSpinner('tips');
  
  // Oznaczenie dla czytników ekranu, że trwa ładowanie
  const tipsPanel = document.getElementById('ai-tips-panel');
  tipsPanel.setAttribute('aria-busy', 'true');
  
  // Dodajemy timeout dla pokazania spinnera
  // Jeśli ładowanie trwa krócej niż 200ms, spinner może migać
  const spinnerTimeout = setTimeout(() => {
    // Pusty callback - spinner będzie widoczny przez co najmniej 200ms
  }, 200);
  
  try {
    // Wywołanie API dla porad AI - zawsze z limitem 3
    const response = await fetch('/ai/tips?limit=3');
    
    // Obsługa błędów HTTP
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    /** @type {AiTip[]} */
    const data = await response.json();
    tipsData = data;
    renderTips();
    
  } catch (error) {
    // Logowanie błędu i aktualizacja stanu
    console.error('Error fetching AI tips:', error);
    errorTips = true;
    showError('tips');
    tipsPanel.setAttribute('aria-busy', 'false');
  } finally {
    loadingTips = false;
    clearTimeout(spinnerTimeout);
  }
}

/**
 * Renderuje dane podsumowania tygodniowego w interfejsie
 * Obsługuje formatowanie kwot i obsługę przypadku braku danych
 */
function renderSummary() {
  if (!summaryData) return;
  
  // Formatowanie kwoty z separatorem tysięcy i 2 miejscami po przecinku
  totalAmount.textContent = summaryData.total_amount.toLocaleString('pl-PL', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
  
  transactionCount.textContent = summaryData.transaction_count.toString();
  
  // Przypadek gdy nie ma transakcji
  if (summaryData.transaction_count === 0) {
    summaryContent.innerHTML = '<p>Brak danych za ten tydzień.</p>';
  }
  
  showContent('summary');
  
  // Oznaczenie aktualizacji dla czytników ekranu
  const weeklyCard = document.getElementById('weekly-summary');
  weeklyCard.setAttribute('aria-busy', 'false');
}

/**
 * Renderuje listę porad AI w interfejsie
 * Obsługuje przypadek braku porad i ograniczenie do maksymalnie 3 porad
 */
function renderTips() {
  if (!tipsData) return;
  
  // Czyścimy listę przed dodaniem nowych elementów
  tipsList.innerHTML = '';
  
  // Przypadek gdy nie ma żadnych porad
  if (tipsData.length === 0) {
    tipsList.innerHTML = '<li class="list-group-item">Brak porad do wyświetlenia.</li>';
  } else {
    // Ograniczamy do maksymalnie 3 porad
    const tipsToShow = tipsData.slice(0, 3);
    
    // Dodajemy każdą poradę jako element listy
    tipsToShow.forEach(tip => {
      const li = document.createElement('li');
      li.className = 'list-group-item';
      li.textContent = tip.message;
      tipsList.appendChild(li);
    });
  }
  
  showContent('tips');
  
  // Oznaczenie aktualizacji dla czytników ekranu
  const tipsPanel = document.getElementById('ai-tips-panel');
  tipsPanel.setAttribute('aria-busy', 'false');
}

/**
 * Funkcja pomocnicza do testowania - symuluje błąd API
 * @param {string} component - 'summary' lub 'tips'
 */
function simulateError(component) {
  if (component === 'summary') {
    errorSummary = true;
    showError('summary');
  } else if (component === 'tips') {
    errorTips = true;
    showError('tips');
  }
}

// Inicjalizacja i obsługa zdarzeń
document.addEventListener('DOMContentLoaded', () => {
  // Inicjalne pobranie danych po załadowaniu strony
  fetchWeeklySummary();
  fetchAiTips();
  
  // Obsługa ponowienia po błędzie dla podsumowania
  summaryRetry.addEventListener('click', (e) => {
    e.preventDefault();
    fetchWeeklySummary();
  });
  
  // Obsługa ponowienia po błędzie dla porad AI
  tipsRetry.addEventListener('click', (e) => {
    e.preventDefault();
    fetchAiTips();
  });
  
  // Dodanie funkcji do window dla testów
  // Dostępne tylko gdy strona jest otwarta z parametrem test=true
  if (window.location.search.includes('test=true')) {
    window.dashboardTest = {
      simulateError,
      fetchWeeklySummary,
      fetchAiTips
    };
  }
}); 