// RBAC Permission Constants for MahaArogya
// Every endpoint checks against these

export const PERMISSIONS = {
  // ── Patient / Own ──────────────────────────────────────────
  PATIENT_VIEW_OWN: 'patient:view:own',
  PATIENT_UPDATE_OWN: 'patient:update:own',
  PATIENT_BOOK_APPOINTMENT: 'patient:book:appointment',
  PATIENT_CANCEL_APPOINTMENT: 'patient:cancel:appointment',
  PATIENT_VIEW_OWN_APPOINTMENTS: 'patient:view:own:appointments',
  PATIENT_USE_AI: 'patient:use:ai',
  PATIENT_VIEW_OWN_TRIAGE: 'patient:view:own:triage',
  PATIENT_VIEW_OWN_TOKEN: 'patient:view:own:token',
  PATIENT_VIEW_OWN_QUEUE: 'patient:view:own:queue',
  PATIENT_VIEW_HOSPITALS: 'patient:view:hospitals',
  PATIENT_SEARCH_LOCATION: 'patient:search:location',
  PATIENT_VIEW_OWN_EMERGENCY: 'patient:view:own:emergency',
  PATIENT_VIEW_OWN_NOTIFICATIONS: 'patient:view:own:notifications',

  // ── Doctor ─────────────────────────────────────────────────
  DOCTOR_VIEW_ASSIGNED_PATIENTS: 'doctor:view:assigned:patients',
  DOCTOR_VIEW_TRIAGE: 'doctor:view:triage',
  DOCTOR_VIEW_QUEUE: 'doctor:view:queue',
  DOCTOR_UPDATE_CONSULTATION: 'doctor:update:consultation',
  DOCTOR_ADD_NOTE: 'doctor:add:note',
  DOCTOR_VIEW_HISTORY: 'doctor:view:history',
  DOCTOR_COMPLETE_CONSULTATION: 'doctor:complete:consultation',

  // ── Nurse ──────────────────────────────────────────────────
  NURSE_VIEW_PATIENTS: 'nurse:view:patients',
  NURSE_VIEW_TRIAGE: 'nurse:view:triage',
  NURSE_UPDATE_PATIENT_STATUS: 'nurse:update:patient:status',
  NURSE_MANAGE_BED_ASSIGNMENTS: 'nurse:manage:bed:assignments',
  NURSE_CONFIRM_CCTV: 'nurse:confirm:cctv',

  // ── Reception ──────────────────────────────────────────────
  RECEPTION_CHECK_IN: 'reception:check:in',
  RECEPTION_MARK_ARRIVED: 'reception:mark:arrived',
  RECEPTION_MANAGE_APPOINTMENTS: 'reception:manage:appointments',
  RECEPTION_MANAGE_TOKENS: 'reception:manage:tokens',
  RECEPTION_VIEW_QUEUE: 'reception:view:queue',
  RECEPTION_VIEW_PATIENT_DEMOGRAPHICS: 'reception:view:patient:demographics',

  // ── Hospital Admin ─────────────────────────────────────────
  HOSPITAL_MANAGE_DEPARTMENTS: 'hospital:manage:departments',
  HOSPITAL_MANAGE_OPD_SLOTS: 'hospital:manage:opd:slots',
  HOSPITAL_MANAGE_STAFF: 'hospital:manage:staff',
  HOSPITAL_VIEW_RESOURCES: 'hospital:view:resources',
  HOSPITAL_MANAGE_BEDS: 'hospital:manage:beds',
  HOSPITAL_VIEW_EMERGENCY: 'hospital:view:emergency',
  HOSPITAL_VIEW_ANALYTICS: 'hospital:view:analytics',
  HOSPITAL_MANAGE_SETTINGS: 'hospital:manage:settings',
  HOSPITAL_CONFIRM_CCTV: 'hospital:confirm:cctv',

  // ── Hospital Head ──────────────────────────────────────────
  HOSPITAL_HEAD_VIEW_ALL: 'hospital_head:view:all',
  HOSPITAL_HEAD_VIEW_PERFORMANCE: 'hospital_head:view:performance',
  HOSPITAL_HEAD_APPROVE_CHANGES: 'hospital_head:approve:changes',

  // ── District Health Officer ────────────────────────────────
  DHO_VIEW_DISTRICT_HOSPITALS: 'dho:view:district:hospitals',
  DHO_VIEW_AGGREGATE_RESOURCES: 'dho:view:aggregate:resources',
  DHO_VIEW_EMERGENCY_LOAD: 'dho:view:emergency:load',
  DHO_VIEW_OPD_STATS: 'dho:view:opd:stats',
  DHO_VIEW_ANALYTICS: 'dho:view:analytics',

  // ── Government ─────────────────────────────────────────────
  GOVT_VIEW_STATE_OVERVIEW: 'govt:view:state:overview',
  GOVT_VIEW_DISTRICTS: 'govt:view:districts',
  GOVT_VIEW_ALL_HOSPITALS: 'govt:view:all:hospitals',
  GOVT_VIEW_AGGREGATE_DATA: 'govt:view:aggregate:data',
  GOVT_VIEW_ANALYTICS: 'govt:view:analytics',

  // ── System Admin ───────────────────────────────────────────
  SYSTEM_MANAGE_USERS: 'system:manage:users',
  SYSTEM_MANAGE_PERMISSIONS: 'system:manage:permissions',
  SYSTEM_VIEW_AUDIT_LOGS: 'system:view:audit:logs',
  SYSTEM_MANAGE_AI_MODELS: 'system:manage:ai:models',
  SYSTEM_MANAGE_CCTV: 'system:manage:cctv',
} as const;

export type PermissionKey = (typeof PERMISSIONS)[keyof typeof PERMISSIONS];

// Role → Permissions mapping
export const ROLE_PERMISSIONS: Record<string, string[]> = {
  PUBLIC_PATIENT: [
    PERMISSIONS.PATIENT_VIEW_OWN,
    PERMISSIONS.PATIENT_UPDATE_OWN,
    PERMISSIONS.PATIENT_BOOK_APPOINTMENT,
    PERMISSIONS.PATIENT_CANCEL_APPOINTMENT,
    PERMISSIONS.PATIENT_VIEW_OWN_APPOINTMENTS,
    PERMISSIONS.PATIENT_USE_AI,
    PERMISSIONS.PATIENT_VIEW_OWN_TRIAGE,
    PERMISSIONS.PATIENT_VIEW_OWN_TOKEN,
    PERMISSIONS.PATIENT_VIEW_OWN_QUEUE,
    PERMISSIONS.PATIENT_VIEW_HOSPITALS,
    PERMISSIONS.PATIENT_SEARCH_LOCATION,
    PERMISSIONS.PATIENT_VIEW_OWN_EMERGENCY,
    PERMISSIONS.PATIENT_VIEW_OWN_NOTIFICATIONS,
  ],
  DOCTOR: [
    PERMISSIONS.DOCTOR_VIEW_ASSIGNED_PATIENTS,
    PERMISSIONS.DOCTOR_VIEW_TRIAGE,
    PERMISSIONS.DOCTOR_VIEW_QUEUE,
    PERMISSIONS.DOCTOR_UPDATE_CONSULTATION,
    PERMISSIONS.DOCTOR_ADD_NOTE,
    PERMISSIONS.DOCTOR_VIEW_HISTORY,
    PERMISSIONS.DOCTOR_COMPLETE_CONSULTATION,
    PERMISSIONS.HOSPITAL_VIEW_ANALYTICS,
  ],
  NURSE: [
    PERMISSIONS.NURSE_VIEW_PATIENTS,
    PERMISSIONS.NURSE_VIEW_TRIAGE,
    PERMISSIONS.NURSE_UPDATE_PATIENT_STATUS,
    PERMISSIONS.NURSE_MANAGE_BED_ASSIGNMENTS,
    PERMISSIONS.NURSE_CONFIRM_CCTV,
  ],
  RECEPTION: [
    PERMISSIONS.RECEPTION_CHECK_IN,
    PERMISSIONS.RECEPTION_MARK_ARRIVED,
    PERMISSIONS.RECEPTION_MANAGE_APPOINTMENTS,
    PERMISSIONS.RECEPTION_MANAGE_TOKENS,
    PERMISSIONS.RECEPTION_VIEW_QUEUE,
    PERMISSIONS.RECEPTION_VIEW_PATIENT_DEMOGRAPHICS,
  ],
  HOSPITAL_ADMIN: [
    PERMISSIONS.HOSPITAL_MANAGE_DEPARTMENTS,
    PERMISSIONS.HOSPITAL_MANAGE_OPD_SLOTS,
    PERMISSIONS.HOSPITAL_MANAGE_STAFF,
    PERMISSIONS.HOSPITAL_VIEW_RESOURCES,
    PERMISSIONS.HOSPITAL_MANAGE_BEDS,
    PERMISSIONS.HOSPITAL_VIEW_EMERGENCY,
    PERMISSIONS.HOSPITAL_VIEW_ANALYTICS,
    PERMISSIONS.HOSPITAL_MANAGE_SETTINGS,
    PERMISSIONS.HOSPITAL_CONFIRM_CCTV,
    PERMISSIONS.RECEPTION_VIEW_QUEUE,
  ],
  HOSPITAL_HEAD: [
    PERMISSIONS.HOSPITAL_HEAD_VIEW_ALL,
    PERMISSIONS.HOSPITAL_HEAD_VIEW_PERFORMANCE,
    PERMISSIONS.HOSPITAL_HEAD_APPROVE_CHANGES,
    PERMISSIONS.HOSPITAL_VIEW_RESOURCES,
    PERMISSIONS.HOSPITAL_VIEW_EMERGENCY,
    PERMISSIONS.HOSPITAL_VIEW_ANALYTICS,
  ],
  DISTRICT_HEALTH_OFFICER: [
    PERMISSIONS.DHO_VIEW_DISTRICT_HOSPITALS,
    PERMISSIONS.DHO_VIEW_AGGREGATE_RESOURCES,
    PERMISSIONS.DHO_VIEW_EMERGENCY_LOAD,
    PERMISSIONS.DHO_VIEW_OPD_STATS,
    PERMISSIONS.DHO_VIEW_ANALYTICS,
  ],
  GOVERNMENT_OFFICIAL: [
    PERMISSIONS.GOVT_VIEW_STATE_OVERVIEW,
    PERMISSIONS.GOVT_VIEW_DISTRICTS,
    PERMISSIONS.GOVT_VIEW_ALL_HOSPITALS,
    PERMISSIONS.GOVT_VIEW_AGGREGATE_DATA,
    PERMISSIONS.GOVT_VIEW_ANALYTICS,
  ],
  SYSTEM_ADMIN: Object.values(PERMISSIONS), // All permissions
};
