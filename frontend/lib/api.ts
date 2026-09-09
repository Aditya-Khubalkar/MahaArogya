/**
 * MahaArogya — Frontend API Client
 * Typed fetch wrapper for all backend endpoints.
 */

const API_BASE = "http://localhost:8000";

/* ─── Types mirroring backend Pydantic schemas ─── */

export interface SymptomDetail {
  name: string;
  severity: string;
  onset: string | null;
  duration: string | null;
  location: string | null;
}

export interface Vitals {
  temperature_c: number | null;
  spo2_percent: number | null;
  heart_rate_bpm: number | null;
  blood_pressure_systolic: number | null;
  blood_pressure_diastolic: number | null;
}

export interface PatientState {
  conversation_id: string;
  language: string;
  modality: string;
  symptoms: Record<string, SymptomDetail>;
  vitals: Vitals;
  age_years: number | null;
  gender: string | null;
  medical_history: string[];
  current_medications: string[];
  allergies: string[];
  raw_utterances: string[];
}

export interface TriageDecision {
  triage_category: "ROUTINE" | "PRIORITY" | "URGENT" | "EMERGENCY";
  triage_confidence: number;
  triggered_rule_ids: string[];
  risk_signals: string[];
  escalation_level: string;
  explanation: string;
  safe_response_text: string;
  model_version: string;
}

export interface Department {
  id: string;
  hospital_id: string;
  name: string;
  open_now: boolean;
  queue_length: number;
  estimated_wait_min: number;
  available_slots: string[];
}

export interface Hospital {
  id: string;
  name: string;
  city: string;
  latitude: number;
  longitude: number;
  departments: Record<string, Department>;
  operating_hours: string;
  emergency_capable: boolean;
  resource_summary: Record<string, unknown>;
  current_load_percent: number;
}

export interface HospitalRecommendation {
  hospital: Hospital;
  department_name: string;
  score: number;
  distance_km: number;
  estimated_wait_min: number;
  explanation: string;
}

export interface ConversationTurnResponse {
  conversation_id: string;
  modality: string;
  language: string;
  transcript_or_text: string;
  ai_response_text: string;
  audio_response_path: string | null;
  patient_state: PatientState;
  triage_decision: TriageDecision;
  is_ready_for_triage: boolean;
  hospital_recommendations: HospitalRecommendation[];
  latency_total_sec: number;
}

export interface OPDToken {
  token_id: string;
  patient_id: string;
  hospital_name: string;
  department_name: string;
  slot_time: string;
  queue_number: number;
  status: string;
  qr_payload: string;
  created_at: string;
}

export interface PatientQueueEntry {
  token_id: string;
  patient_id: string;
  hospital_id: string;
  department_name: string;
  queue_number: number;
  arrival_status: string;
  checked_in_at: string | null;
  notes: string | null;
}

export interface CCTVOccupancyResult {
  camera_id: string;
  ward_id: string;
  estimated_occupied_beds: number;
  total_beds: number;
  occupancy_percentage: number;
  confidence_score: number;
  db_authoritative_occupied: number;
  discrepancy_detected: boolean;
  discrepancy_delta: number;
  human_verification_required: boolean;
  timestamp: string;
}

export interface HealthStatus {
  status: string;
  subsystem: string;
  gpu_detected: string;
  version: string;
}

/* ─── API Functions ─── */

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(`API Error ${res.status}: ${err}`);
  }
  return res.json();
}

export async function checkHealth(): Promise<HealthStatus> {
  return apiFetch<HealthStatus>("/health");
}

export async function sendConversationTurn(params: {
  conversation_id?: string;
  text_input: string;
  language?: string;
  patient_lat?: number;
  patient_lon?: number;
}): Promise<ConversationTurnResponse> {
  return apiFetch<ConversationTurnResponse>("/api/v1/conversation/turn", {
    method: "POST",
    body: JSON.stringify({
      text_input: params.text_input,
      language: params.language ?? "mr",
      patient_lat: params.patient_lat ?? 19.01,
      patient_lon: params.patient_lon ?? 72.85,
      ...(params.conversation_id && { conversation_id: params.conversation_id }),
    }),
  });
}

export async function issueOPDToken(params: {
  patient_id: string;
  hospital_name: string;
  department_name: string;
  slot_time: string;
  current_queue_length?: number;
}): Promise<OPDToken> {
  return apiFetch<OPDToken>("/api/v1/opd/issue_token", {
    method: "POST",
    body: JSON.stringify({
      patient_id: params.patient_id,
      hospital_name: params.hospital_name,
      department_name: params.department_name,
      slot_time: params.slot_time,
      current_queue_length: params.current_queue_length ?? 5,
    }),
  });
}

export async function checkinPatient(params: {
  token_id: string;
  staff_user_id?: string;
}): Promise<PatientQueueEntry> {
  return apiFetch<PatientQueueEntry>("/api/v1/reception/checkin", {
    method: "POST",
    body: JSON.stringify({
      token_id: params.token_id,
      staff_user_id: params.staff_user_id ?? "reception_staff_01",
    }),
  });
}

export async function estimateCCTV(params: {
  camera_id: string;
  ward_id: string;
  detected_occupied_beds: number;
  total_beds: number;
  db_authoritative_occupied: number;
  confidence?: number;
}): Promise<CCTVOccupancyResult> {
  return apiFetch<CCTVOccupancyResult>("/api/v1/cctv/estimate", {
    method: "POST",
    body: JSON.stringify({
      camera_id: params.camera_id,
      ward_id: params.ward_id,
      detected_occupied_beds: params.detected_occupied_beds,
      total_beds: params.total_beds,
      db_authoritative_occupied: params.db_authoritative_occupied,
      confidence: params.confidence ?? 0.88,
    }),
  });
}

export interface QueueItem {
  token_id: string;
  patient_name: string;
  status: string;
  department: string;
  estimated_wait_time: number;
}

export interface RoleInfo {
  id: string;
  title: string;
  description: string;
  permissions: string[];
}

export async function getHospitals(): Promise<Hospital[]> {
  return apiFetch<Hospital[]>("/api/v1/hospitals/");
}

export async function getQueue(): Promise<QueueItem[]> {
  return apiFetch<QueueItem[]>("/api/v1/queue/");
}

export async function getRoles(): Promise<RoleInfo[]> {
  return apiFetch<RoleInfo[]>("/api/v1/roles/");
}

export async function demoLogin(userId: string): Promise<any> {
  return apiFetch<any>("/api/v1/auth/demo-login", {
    method: "POST",
    body: JSON.stringify({ user_id: userId }),
  });
}

export async function getDashboardStats(): Promise<any> {
  return apiFetch<any>("/api/v1/dashboard/stats");
}

export async function getWardPatients(): Promise<any[]> {
  return apiFetch<any[]>("/api/v1/ward/patients");
}

export async function getDoctorQueue(): Promise<any[]> {
  return apiFetch<any[]>("/api/v1/doctor/queue");
}

export async function getAdminOverview(): Promise<any> {
  return apiFetch<any>("/api/v1/admin/overview");
}

export async function getGovtOverview(): Promise<any> {
  return apiFetch<any>("/api/v1/govt/state-overview");
}

export async function getLiveQueue(): Promise<QueueItem[]> {
  return apiFetch<QueueItem[]>("/api/v1/queue/live");
}

