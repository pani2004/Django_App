export interface Organization {
  id: number;
  name: string;
  slug: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  role: string;
  organization: Organization;
}

export interface LoginResponse {
  access: string;
  refresh: string;
}

export interface EmissionEstimate {
  method: string;
  factor_source: string;
  factor_value: string;
  co2e_kg: string;
  co2e_tonnes: string;
  confidence: "high" | "medium" | "low";
}

export interface IngestionBatch {
  id: number;
  source: string;
  filename: string;
  status: string;
  row_count_total: number;
  row_count_success: number;
  row_count_failed: number;
  error_summary: { row: number; errors: string[] }[];
  uploaded_by_email: string;
  created_at: string;
  completed_at: string | null;
}

export interface RawRow {
  row_number: number;
  raw_data: Record<string, string>;
  parse_errors: string[];
}

export interface Activity {
  id: number;
  batch: number;
  batch_source: string;
  scope: string;
  scope_category: string;
  activity_type: string;
  activity_value: string | null;
  activity_unit: string;
  facility_code: string;
  period_start: string | null;
  period_end: string | null;
  source_system: string;
  source_record_id: string;
  review_status: string;
  quality_flags: string[];
  is_locked: boolean;
  emission?: EmissionEstimate;
  created_at: string;
}

export interface ActivityDetail extends Activity {
  raw_row?: RawRow;
  original_value: string | null;
  original_unit: string;
  cost_center: string;
  vendor_id: string;
}

export interface AuditLogEntry {
  id: number;
  entity_type: string;
  entity_id: string;
  action: string;
  actor_email: string;
  timestamp: string;
  before: Record<string, unknown>;
  after: Record<string, unknown>;
  reason: string;
}

export interface DashboardStats {
  pending_review: number;
  flagged: number;
  approved_locked: number;
  needs_attention: number;
  failed_batches: number;
  by_scope: Record<string, number>;
  by_status: Record<string, number>;
}

export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
