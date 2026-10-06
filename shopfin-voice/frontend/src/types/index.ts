export interface User { id: number; name: string; email: string; shop: string | null; business_type: string | null }
export interface Transaction { id: number; date: string; type: string; category: string; description: string; method: string; amount: number; status: string; notes?: string | null }
export interface BudgetItem { id: number; name: string; spent: number; limit: number; percentage: number; status: 'Healthy' | 'Warning' | 'Exceeded' }
export interface SavingsGoal { id: number; name: string; target_amount: number; current_amount: number; target_date: string | null; monthly_contribution: number; progress: number }
export interface Deposit { id: number; goal_id: number; goal_name: string; amount: number; date: string; note: string }
export interface Insight { id: string; tone: 'info' | 'warn' | 'good'; text: string }
export interface DayPoint { d: string; date: string; sales: number; exp: number }
export interface DashboardData {
  today_sales: number; today_expenses: number; sales_change: number | null; expenses_change: number | null
  available_cash: number; estimated_surplus: number; total_sales: number; total_expenses: number
  budget_total: number; budget_used: number; savings_total: number; weekly: DayPoint[]
  opening_cash: number; cash_after_savings: number
  today_sales_count: number; today_average_sale: number; today_by_method: Slice[]
}
export interface ReportData { period: string; start: string; end: string; total_sales: number; total_expenses: number; estimated_surplus: number; top_expense_category: string | null; budget_used: number; savings_total: number }
export interface CommandResult { ok: boolean; intent: string; message: string; warning: string | null; data: Record<string, unknown> | null }

// ---- Business dashboards ----
export interface Point { date: string; label: string; amount: number }
export interface Slice { name: string; amount: number; share: number }
export interface RecentTx { id: number; date: string; type: string; category: string; description: string; method: string; amount: number }
export interface FlowDashboard {
  days: number; start: string; end: string
  today: number; yesterday: number; today_change: number | null
  week: number; prev_week: number; week_change: number | null
  month: number; prev_month: number; month_change: number | null
  today_count: number; today_average: number; range_total: number; daily_average: number
  best_day: Point | null; daily: Point[]; by_method: Slice[]; by_category: Slice[]; recent: RecentTx[]
  budget_total?: number; budget_used_percent?: number
}
export interface FlowPoint { date: string; label: string; money_in: number; money_out: number; net: number; balance: number }
export interface MethodBalance { name: string; money_in: number; money_out: number; balance: number }
export interface CashDashboard {
  days: number; opening_cash: number; total_in: number; total_out: number; available_cash: number
  savings_total: number; cash_after_savings: number; cash_in_hand: number; digital_balance: number
  month_in: number; month_out: number; month_net: number; avg_daily_spend: number; runway_days: number | null
  by_method: MethodBalance[]; flow: FlowPoint[]
}
export interface BudgetOverviewItem extends BudgetItem { remaining: number; projected: number; projected_percentage: number }
export interface BudgetOverview {
  month: string; day_of_month: number; days_in_month: number; days_left: number
  total_limit: number; total_spent: number; remaining: number; percentage: number
  daily_burn: number; projected_spend: number; projected_percentage: number; safe_daily_spend: number
  counts: { Healthy: number; Warning: number; Exceeded: number }
  items: BudgetOverviewItem[]; unbudgeted: { category: string; spent: number }[]
}
