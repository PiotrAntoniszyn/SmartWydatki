/**
 * Utility functions for mapping between API expense data and view models
 */

import type { ExpenseVM, CategoryVM } from '../types/expenses';

/**
 * Interface matching the ExpenseRead DTO from the server
 */
interface ExpenseDTO {
  id: string;
  amount: number;
  description: string | null;
  category_id: string;
  date_of_expense: string;
  created_at: string;
}

/**
 * Interface matching the CategoryRead DTO from the server
 */
interface CategoryDTO {
  id: string;
  name: string;
  is_default: boolean;
}

/**
 * Maps an API expense DTO to a view model
 */
export const mapExpenseToViewModel = (
  expense: ExpenseDTO, 
  categories: CategoryVM[] = []
): ExpenseVM => {
  // Find category name if categories are provided
  const category = categories.find(c => c.id === expense.category_id);
  
  // Convert ISO date to display format (DD/MM/YYYY)
  const expenseDate = new Date(expense.date_of_expense);
  const formattedDate = expenseDate.toLocaleDateString('pl-PL', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  });
  
  return {
    id: expense.id,
    amount: expense.amount,
    description: expense.description || '',
    categoryId: expense.category_id,
    date: formattedDate,
    datetime: expense.date_of_expense,
    createdAt: expense.created_at,
    categoryName: category?.name || 'Nieznana kategoria'
  };
};

/**
 * Maps a list of API expense DTOs to view models
 */
export const mapExpensesToViewModels = (
  expenses: ExpenseDTO[], 
  categories: CategoryVM[] = []
): ExpenseVM[] => {
  return expenses.map(expense => mapExpenseToViewModel(expense, categories));
};

/**
 * Maps an expense view model to an API create/update DTO
 */
export const mapViewModelToExpenseDTO = (expense: ExpenseVM): any => {
  // For API, we need to convert the datetime to the expected format
  // and use snake_case property names
  return {
    amount: expense.amount,
    description: expense.description,
    category_id: expense.categoryId,
    // Use the ISO datetime string for the API
    date_of_expense: expense.datetime
  };
};

/**
 * Maps an API category DTO to a view model
 */
export const mapCategoryToViewModel = (category: CategoryDTO): CategoryVM => {
  return {
    id: category.id,
    name: category.name,
    isDefault: category.is_default
  };
};

/**
 * Maps a list of API category DTOs to view models
 */
export const mapCategoriesToViewModels = (categories: CategoryDTO[]): CategoryVM[] => {
  return categories.map(mapCategoryToViewModel);
}; 