/**
 * Categories Page – Zarządzanie kategoriami wydatków
 * --------------------------------------------------
 * Ten skrypt odpowiada za:
 * 1. Pobieranie listy kategorii z API
 * 2. Renderowanie stanów UI (ładowanie, pusto, lista, błąd)
 * 3. Obsługę przycisków "Dodaj", "Edytuj", "Usuń" (w tym otwieranie modali)
 *
 * W dalszych krokach zostaną zaimplementowane:
 * - Formularz CategoryFormModal z walidacją inline
 * - ConfirmDialog do potwierdzania usunięcia
 * - Zarządzanie stanem optimistycznym dla operacji CRUD
 * --------------------------------------------------
 * QA checklist (do uzupełnienia w kolejnych iteracjach):
 * - [ ] Poprawne wyświetlanie spinnera (>200 ms)
 * - [ ] Walidacja dostępności (ARIA)
 * - [ ] Obsługa błędów HTTP 400/404/409/500
 */

(() => {
  /* -------------------------- CONSTANTS & HELPERS ------------------------- */
  const API_BASE = '/categories'; // API endpoint base path
  const MIN_SPINNER_MS = 200;

  /**
   * Tworzy element <td> z textContent i opcjonalnymi klasami.
   * @param {string} text
   * @param {string[]} [classList]
   * @returns {HTMLTableCellElement}
   */
  function createCell(text, classList = []) {
    const td = document.createElement('td');
    td.textContent = text;
    classList.forEach((c) => td.classList.add(c));
    return td;
  }

  /**
   * Dodaje klasę d-none i ustawia aria-hidden.
   */
  function hide(el) {
    el.classList.add('d-none');
    el.setAttribute('aria-hidden', 'true');
  }

  /**
   * Usuwa klasę d-none i ustawia aria-hidden.
   */
  function show(el) {
    el.classList.remove('d-none');
    el.setAttribute('aria-hidden', 'false');
  }

  /**
   * Pokazuje spinner wewnątrz przycisku i blokuje go na czas akcji async.
   * @template T
   * @param {HTMLButtonElement} button
   * @param {() => Promise<T>} action
   * @returns {Promise<T>}
   */
  async function withButtonSpinner(button, action) {
    const originalContent = button.innerHTML;
    const originalDisabled = button.disabled;
    root.setAttribute('aria-busy', 'true');
    button.disabled = true;
    button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
    try {
      return await action();
    } finally {
      button.innerHTML = originalContent;
      button.disabled = originalDisabled;
      root.setAttribute('aria-busy', 'false');
    }
  }

  /* ------------------------------ STATE ----------------------------------- */
  const state = {
    categories: /** @type {CategoryListItem[]} */ ([]),
    loading: false,
    error: false,
  };

  /* ---------------------------- ELEMENTS ---------------------------------- */
  const root = document.getElementById('categories-page');
  if (!root) {
    // Nie jesteśmy na stronie kategorii – nie inicjalizujemy skryptu
    return;
  }

  const btnAdd = /** @type {HTMLButtonElement} */ (document.getElementById('add-category-btn'));
  const loadingEl = document.getElementById('categories-loading');
  const errorEl = document.getElementById('categories-error');
  const retryBtn = /** @type {HTMLButtonElement} */ (document.getElementById('categories-retry-btn'));
  const emptyEl = document.getElementById('categories-empty');
  const emptyAddBtn = /** @type {HTMLButtonElement} */ (document.getElementById('categories-add-empty-btn'));
  const listWrapper = document.getElementById('categories-list-wrapper');
  const tbody = /** @type {HTMLTableSectionElement} */ (document.getElementById('categories-tbody'));

  /* --------------------------- API ACTIONS -------------------------------- */

  /** @returns {Promise<CategoryListItem[]>} */
  async function apiFetchCategories() {
    const res = await fetch(API_BASE, {
      headers: {
        'Accept': 'application/json',
      },
    });
    if (!res.ok) throw res;
    /** @type {CategoryRead[]} */
    const data = await res.json();
    return data.map((c) => ({
      id: c.id,
      name: c.name,
      is_default: c.is_default,
    }));
  }

  /**
   * @param {{ name: string }} payload
   * @returns {Promise<CategoryListItem>}
   */
  async function apiCreateCategory(payload) {
    const res = await fetch(API_BASE, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw res;
    return res.json();
  }

  /**
   * @param {string} id
   * @param {{ name: string }} payload
   */
  async function apiUpdateCategory(id, payload) {
    const res = await fetch(`${API_BASE}/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw res;
    return res.json();
  }

  /**
   * @param {string} id
   */
  async function apiDeleteCategory(id) {
    const res = await fetch(`${API_BASE}/${id}`, {
      method: 'DELETE',
      headers: {
        'Accept': 'application/json',
      },
    });
    if (!res.ok) throw res;
  }

  /* --------------------------- RENDERERS ---------------------------------- */

  function render() {
    if (state.loading) {
      show(loadingEl);
      hide(errorEl);
      hide(emptyEl);
      hide(listWrapper);
      return;
    }

    hide(loadingEl);

    if (state.error) {
      show(errorEl);
      hide(emptyEl);
      hide(listWrapper);
      return;
    }

    if (state.categories.length === 0) {
      show(emptyEl);
      hide(listWrapper);
      return;
    }

    hide(emptyEl);
    show(listWrapper);

    // Render list items
    tbody.innerHTML = '';
    state.categories.forEach((cat) => {
      const tr = document.createElement('tr');
      tr.setAttribute('data-id', cat.id);

      // Nazwa kategorii
      tr.appendChild(createCell(cat.name));

      // is_default badge
      const tdDefault = createCell('', ['text-center']);
      if (cat.is_default) {
        const defaultBadge = document.createElement('span');
        defaultBadge.className = 'badge bg-secondary';
        defaultBadge.textContent = 'domyślna';
        tdDefault.appendChild(defaultBadge);
      }
      tr.appendChild(tdDefault);

      // Action buttons
      const tdActions = document.createElement('td');
      tdActions.className = 'text-end';

      const editBtn = document.createElement('button');
      editBtn.className = 'btn btn-sm btn-outline-primary me-2';
      editBtn.setAttribute('aria-label', `Edytuj kategorię ${cat.name}`);
      editBtn.innerHTML = '<i class="bi bi-pencil"></i>';
      editBtn.addEventListener('click', (e) => onEdit(cat.id, /** @type {HTMLButtonElement} */ (e.currentTarget)));

      const deleteBtn = document.createElement('button');
      deleteBtn.className = 'btn btn-sm btn-outline-danger';
      deleteBtn.setAttribute('aria-label', `Usuń kategorię ${cat.name}`);
      deleteBtn.innerHTML = '<i class="bi bi-trash"></i>';
      deleteBtn.disabled = cat.is_default; // Nie można usunąć domyślnej
      deleteBtn.addEventListener('click', (e) => onDelete(cat.id, /** @type {HTMLButtonElement} */ (e.currentTarget)));

      tdActions.appendChild(editBtn);
      tdActions.appendChild(deleteBtn);
      tr.appendChild(tdActions);

      tbody.appendChild(tr);
    });
  }

  /* ------------------------- MODAL COMPONENTS ----------------------------- */

  /**
   * Tworzy i otwiera prosty modal formularza kategorii.
   * Zwraca Promise rozwiązywane danymi formularza lub null (anulowanie).
   * @param {('create'|'edit')} mode
   * @param {CategoryFormData=} initialData
   * @returns {Promise<CategoryFormData|null>}
   */
  function openCategoryFormModal(mode, initialData = {}) {
    return new Promise((resolve) => {
      const previouslyFocused = /** @type {HTMLElement} */ (document.activeElement);

      const backdrop = document.createElement('div');
      backdrop.className = 'modal-backdrop fade show';

      const modal = document.createElement('div');
      modal.className = 'modal d-block';
      modal.setAttribute('role', 'dialog');
      modal.setAttribute('aria-modal', 'true');
      modal.setAttribute('aria-labelledby', 'category-modal-title');

      modal.innerHTML = `
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title" id="category-modal-title">${mode === 'create' ? 'Dodaj kategorię' : 'Edytuj kategorię'}</h5>
              <button type="button" class="btn-close" aria-label="Zamknij"></button>
            </div>
            <div class="modal-body">
              <form id="category-form" novalidate>
                <div class="mb-3">
                  <label for="category-name-input" class="form-label">Nazwa kategorii</label>
                  <input type="text" class="form-control" id="category-name-input" maxlength="30" required value="${initialData.name || ''}">
                  <div class="invalid-feedback" id="category-name-error"></div>
                </div>
              </form>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" id="cancel-btn">Anuluj</button>
              <button type="button" class="btn btn-primary" id="save-btn">Zapisz</button>
            </div>
          </div>
        </div>`;

      const portal = document.getElementById('modal-portal-root');
      portal.appendChild(backdrop);
      portal.appendChild(modal);

      // Focus trap – ustaw focus na input przy otwarciu
      const nameInput = modal.querySelector('#category-name-input');
      nameInput.focus();

      // Zamknięcie modalu
      function close(result = null) {
        portal.removeChild(modal);
        portal.removeChild(backdrop);
        if (previouslyFocused) previouslyFocused.focus();
        resolve(result);
      }

      // Walidacja nazwy
      function validateName(value) {
        if (!value.trim()) {
          return 'Nazwa nie może być pusta.';
        }
        if (value.length > 30) {
          return 'Nazwa może mieć maksymalnie 30 znaków.';
        }
        const exists = state.categories.some((c) => c.name.toLowerCase() === value.trim().toLowerCase() && c.id !== initialData.id);
        if (exists) {
          return 'Kategoria o tej nazwie już istnieje.';
        }
        return null;
      }

      function showInputError(msg) {
        const errorEl = modal.querySelector('#category-name-error');
        errorEl.textContent = msg;
        nameInput.classList.add('is-invalid');
      }

      function clearInputError() {
        const errorEl = modal.querySelector('#category-name-error');
        errorEl.textContent = '';
        nameInput.classList.remove('is-invalid');
      }

      // Event listeners
      modal.querySelector('.btn-close').addEventListener('click', () => close());
      modal.querySelector('#cancel-btn').addEventListener('click', () => close());

      modal.querySelector('#save-btn').addEventListener('click', () => {
        const value = nameInput.value.trim();
        const err = validateName(value);
        if (err) {
          showInputError(err);
          return;
        }
        clearInputError();
        /** @type {CategoryFormData} */
        const result = { id: initialData.id, name: value };
        close(result);
      });

      nameInput.addEventListener('input', () => {
        if (nameInput.classList.contains('is-invalid')) {
          clearInputError();
        }
      });

      // Escape key closes modal
      modal.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
          e.preventDefault();
          close();
        }
      });
    });
  }

  /**
   * Wyświetla okno potwierdzenia. Zwraca Promise<boolean> (true -> potwierdzono).
   * @param {string} message
   */
  function openConfirmDialog(message) {
    return new Promise((resolve) => {
      const previouslyFocused = /** @type {HTMLElement} */ (document.activeElement);

      const backdrop = document.createElement('div');
      backdrop.className = 'modal-backdrop fade show';

      const modal = document.createElement('div');
      modal.className = 'modal d-block';
      modal.setAttribute('role', 'dialog');
      modal.setAttribute('aria-modal', 'true');

      modal.innerHTML = `
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">Potwierdzenie</h5>
            </div>
            <div class="modal-body">
              <p>${message}</p>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" id="cancel-confirm">Anuluj</button>
              <button type="button" class="btn btn-danger" id="ok-confirm">OK</button>
            </div>
          </div>
        </div>`;

      const portal = document.getElementById('modal-portal-root');
      portal.appendChild(backdrop);
      portal.appendChild(modal);

      function close(result) {
        portal.removeChild(modal);
        portal.removeChild(backdrop);
        if (previouslyFocused) previouslyFocused.focus();
        resolve(result);
      }

      modal.querySelector('#cancel-confirm').addEventListener('click', () => close(false));
      modal.querySelector('#ok-confirm').addEventListener('click', () => close(true));

      modal.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
          e.preventDefault();
          close(false);
        }
      });
    });
  }

  /**
   * Globalny dialog błędu – wyświetla komunikat i przycisk OK.
   * Zwraca Promise<void> po zamknięciu.
   * @param {string} message
   */
  function openErrorDialog(message) {
    return new Promise((resolve) => {
      const previouslyFocused = /** @type {HTMLElement} */ (document.activeElement);

      const backdrop = document.createElement('div');
      backdrop.className = 'modal-backdrop fade show';

      const modal = document.createElement('div');
      modal.className = 'modal d-block';
      modal.setAttribute('role', 'alertdialog');
      modal.setAttribute('aria-modal', 'true');

      modal.innerHTML = `
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">Błąd</h5>
            </div>
            <div class="modal-body">
              <p>${message}</p>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-primary" id="error-ok">OK</button>
            </div>
          </div>
        </div>`;

      const portal = document.getElementById('modal-portal-root');
      portal.appendChild(backdrop);
      portal.appendChild(modal);

      function close() {
        portal.removeChild(modal);
        portal.removeChild(backdrop);
        if (previouslyFocused) previouslyFocused.focus();
        resolve();
      }

      modal.querySelector('#error-ok').addEventListener('click', close);
      modal.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' || e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          close();
        }
      });
    });
  }

  /**
   * Mapowanie błędu HTTP na czytelny komunikat.
   * @param {Response} res
   */
  async function mapApiError(res) {
    let msg = `Błąd: ${res.status}`;
    try {
      const data = await res.json();
      if (data && data.error) msg = data.error;
    } catch (_) {}
    return msg;
  }

  // Zamiana alert() w mapowaniach błędów na modal --------------------------

  async function showApiError(res) {
    const msg = await mapApiError(res);
    await openErrorDialog(msg);
  }

  /* ------------------------- EVENT HANDLERS ------------------------------- */

  function onAdd(triggerBtn = btnAdd) {
    openCategoryFormModal('create').then(async (formData) => {
      if (!formData) return; // anulowano
      await withButtonSpinner(triggerBtn, async () => {
        try {
          const created = await apiCreateCategory({ name: formData.name });
          state.categories.push(created);
          render();
        } catch (err) {
          console.error('Create error', err);
          if (err instanceof Response) {
            await showApiError(err);
          }
        }
      });
    });
  }

  /**
   * @param {string} id
   */
  function onEdit(id, triggerBtn) {
    const existing = state.categories.find((c) => c.id === id);
    if (!existing) return;
    openCategoryFormModal('edit', existing).then(async (formData) => {
      if (!formData) return; // anulowano
      await withButtonSpinner(triggerBtn, async () => {
        try {
          const updated = await apiUpdateCategory(id, { name: formData.name });
          const idx = state.categories.findIndex((c) => c.id === id);
          if (idx >= 0) state.categories[idx] = updated;
          render();
        } catch (err) {
          console.error('Update error', err);
          if (err instanceof Response) {
            await showApiError(err);
          }
        }
      });
    });
  }

  /**
   * @param {string} id
   */
  function onDelete(id, triggerBtn) {
    const cat = state.categories.find((c) => c.id === id);
    if (!cat) return;
    openConfirmDialog(`Czy na pewno chcesz usunąć kategorię "${cat.name}"?`).then(async (confirmed) => {
      if (!confirmed) return;
      await withButtonSpinner(triggerBtn, async () => {
        try {
          await apiDeleteCategory(id);
          state.categories = state.categories.filter((c) => c.id !== id);
          render();
        } catch (err) {
          console.error('Delete error', err);
          if (err instanceof Response) {
            await showApiError(err);
          }
        }
      });
    });
  }

  /* ----------------------------- FLOW ------------------------------------- */

  async function loadCategories() {
    state.loading = true;
    state.error = false;
    root.setAttribute('aria-busy', 'true');
    render();

    const startTime = Date.now();

    try {
      const cats = await apiFetchCategories();
      state.categories = cats;
    } catch (err) {
      console.error('Failed to load categories', err);
      state.error = true;
    } finally {
      // Minimalne wyświetlanie spinnera
      const elapsed = Date.now() - startTime;
      if (elapsed < MIN_SPINNER_MS) {
        await new Promise((r) => setTimeout(r, MIN_SPINNER_MS - elapsed));
      }
      state.loading = false;
      root.setAttribute('aria-busy', 'false');
      render();
    }
  }

  /* ----------------------------- INIT ------------------------------------- */

  function init() {
    // Początkowe renderowanie
    render();
    loadCategories();

    // Event listeners
    btnAdd.addEventListener('click', (e) => onAdd(e.currentTarget));
    emptyAddBtn.addEventListener('click', (e) => onAdd(e.currentTarget));
    retryBtn.addEventListener('click', loadCategories);
  }

  // Typy JSDoc dla lepszej edycji/IDE ------------------------------------
  /**
   * @typedef {{ id: string, name: string, is_default: boolean }} CategoryListItem
   */

  /**
   * @typedef {{ id: string, name: string, is_default: boolean }} CategoryRead
   */

  document.addEventListener('DOMContentLoaded', init);
})(); 