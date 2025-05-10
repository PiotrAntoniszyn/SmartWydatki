/**
 * Testy dla widoku Dashboard
 * 
 * Uruchamianie: 
 * 1. Uruchom aplikację w trybie testowym
 * 2. Otwórz przeglądarkę z adresem http://localhost:5000/dashboard?test=true
 * 3. Uruchom testy z konsoli:
 *    mocha tests/dashboard.test.js
 */

describe('Dashboard View Tests', function() {
  // Ustawiamy dłuższy timeout, ponieważ testy mogą wymagać ładowania
  this.timeout(5000);
  
  beforeEach(function() {
    // Przygotuj środowisko testowe
    cy.visit('/dashboard?test=true');
    cy.window().then(win => {
      expect(win.dashboardTest).to.exist;
    });
  });
  
  describe('Tygodniowe podsumowanie wydatków', function() {
    it('powinno wyświetlić spinner podczas ładowania', function() {
      cy.get('#summary-spinner').should('be.visible');
      cy.get('#summary-content').should('not.be.visible');
      cy.get('#summary-error').should('not.be.visible');
    });
    
    it('powinno wyświetlić dane po poprawnym załadowaniu', function() {
      // Poczekaj na zakończenie ładowania
      cy.get('#summary-content').should('be.visible', { timeout: 5000 });
      cy.get('#total-amount').should('exist');
      cy.get('#transaction-count').should('exist');
    });
    
    it('powinno obsłużyć błąd i umożliwić ponowienie', function() {
      cy.window().then(win => {
        win.dashboardTest.simulateError('summary');
      });
      
      cy.get('#summary-error').should('be.visible');
      cy.get('#summary-retry').should('exist').click();
      cy.get('#summary-spinner').should('be.visible');
      
      // Sprawdź, czy po ponowieniu pojawią się dane
      cy.get('#summary-content').should('be.visible', { timeout: 5000 });
    });
    
    it('powinno wyświetlić informację, gdy brak transakcji', function() {
      // Mockowanie pustej odpowiedzi
      cy.intercept('/expenses/summary?period=weekly', {
        statusCode: 200,
        body: { total_amount: 0, transaction_count: 0 }
      }).as('emptySummary');
      
      cy.window().then(win => {
        win.dashboardTest.fetchWeeklySummary();
      });
      
      cy.wait('@emptySummary');
      cy.get('#summary-content').should('contain.text', 'Brak danych za ten tydzień');
    });
  });
  
  describe('Panel porad AI', function() {
    it('powinien wyświetlić spinner podczas ładowania', function() {
      cy.get('#tips-spinner').should('be.visible');
      cy.get('#tips-content').should('not.be.visible');
      cy.get('#tips-error').should('not.be.visible');
    });
    
    it('powinien wyświetlić porady po poprawnym załadowaniu', function() {
      // Poczekaj na zakończenie ładowania
      cy.get('#tips-content').should('be.visible', { timeout: 5000 });
      cy.get('#tips-list li').should('have.length.greaterThan', 0);
    });
    
    it('powinien obsłużyć błąd i umożliwić ponowienie', function() {
      cy.window().then(win => {
        win.dashboardTest.simulateError('tips');
      });
      
      cy.get('#tips-error').should('be.visible');
      cy.get('#tips-retry').should('exist').click();
      cy.get('#tips-spinner').should('be.visible');
      
      // Sprawdź, czy po ponowieniu pojawią się dane
      cy.get('#tips-content').should('be.visible', { timeout: 5000 });
    });
    
    it('powinien wyświetlić maksymalnie 3 porady', function() {
      // Mockowanie odpowiedzi z większą liczbą porad
      cy.intercept('/ai/tips?limit=3', {
        statusCode: 200,
        body: [
          { message: 'Porada 1' },
          { message: 'Porada 2' },
          { message: 'Porada 3' },
          { message: 'Porada 4' },
          { message: 'Porada 5' }
        ]
      }).as('manyTips');
      
      cy.window().then(win => {
        win.dashboardTest.fetchAiTips();
      });
      
      cy.wait('@manyTips');
      cy.get('#tips-list li').should('have.length', 3);
    });
  });
  
  describe('Dostępność', function() {
    it('powinien mieć odpowiednie atrybuty ARIA', function() {
      cy.get('[aria-live]').should('have.length.greaterThan', 0);
      cy.get('[aria-labelledby]').should('have.length.greaterThan', 0);
      cy.get('[aria-hidden]').should('have.length.greaterThan', 0);
      cy.get('[aria-busy]').should('have.length.greaterThan', 0);
    });
    
    it('powinien mieć fokusowalne nagłówki', function() {
      cy.get('h1[tabindex="-1"]').should('exist');
    });
    
    it('powinien mieć opisane przyciski', function() {
      cy.get('button[aria-label]').should('have.length.greaterThan', 0);
    });
  });
}); 