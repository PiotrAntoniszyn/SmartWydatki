export interface ExpenseVM {
  id: string;
  amount: number;
  description: string;
  categoryId: string;
  date: string; // 'DD/MM/YYYY' format for display
  datetime: string; // ISO format for API
  createdAt: string; // ISO format
  categoryName?: string; // Optional category name for display
}

export interface CategoryVM {
  id: string;
  name: string;
  isDefault: boolean;
}

export interface FilterParams {
  search: string;
  dateFrom: string | null; // ISO format
  dateTo: string | null; // ISO format
  amountMin: number | null;
  amountMax: number | null;
}

export interface PaginationVM {
  limit: number;
  offset: number;
  total: number;
  currentPage: number;
  totalPages: number;
}

export interface ExpenseFormData {
  id?: string;
  amount: number;
  description: string;
  categoryId: string;
  date: string; // ISO format
} 