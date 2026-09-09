-- CreateEnum
CREATE TYPE "UserRole" AS ENUM ('PUBLIC_PATIENT', 'DOCTOR', 'NURSE', 'RECEPTION', 'HOSPITAL_ADMIN', 'HOSPITAL_HEAD', 'DISTRICT_HEALTH_OFFICER', 'GOVERNMENT_OFFICIAL', 'SYSTEM_ADMIN');

-- CreateEnum
CREATE TYPE "HospitalStatus" AS ENUM ('ACTIVE', 'INACTIVE', 'EMERGENCY_ONLY', 'UNDER_MAINTENANCE');

-- CreateEnum
CREATE TYPE "DepartmentStatus" AS ENUM ('ACTIVE', 'INACTIVE', 'TEMPORARILY_CLOSED');

-- CreateEnum
CREATE TYPE "BedType" AS ENUM ('GENERAL_BED', 'ICU_BED', 'EMERGENCY_BED', 'MATERNITY_BED', 'PEDIATRIC_BED', 'ISOLATION_BED', 'OTHER');

-- CreateEnum
CREATE TYPE "BedStatus" AS ENUM ('AVAILABLE', 'OCCUPIED', 'RESERVED', 'HELD', 'MAINTENANCE', 'UNKNOWN');

-- CreateEnum
CREATE TYPE "ResourceType" AS ENUM ('OXYGEN_CYLINDER', 'OXYGEN_CONCENTRATOR', 'VENTILATOR', 'DEFIBRILLATOR', 'ECG_MACHINE', 'INFUSION_PUMP', 'OTHER');

-- CreateEnum
CREATE TYPE "ResourceStatus" AS ENUM ('AVAILABLE', 'IN_USE', 'HELD', 'MAINTENANCE', 'UNAVAILABLE');

-- CreateEnum
CREATE TYPE "AppointmentStatus" AS ENUM ('BOOKED', 'CONFIRMED', 'ARRIVED', 'IN_CONSULTATION', 'COMPLETED', 'CANCELLED', 'NO_SHOW', 'RESCHEDULED');

-- CreateEnum
CREATE TYPE "OPDSlotStatus" AS ENUM ('OPEN', 'NEAR_FULL', 'FULL', 'CLOSED', 'CANCELLED');

-- CreateEnum
CREATE TYPE "TokenStatus" AS ENUM ('GENERATED', 'CALLED', 'IN_PROGRESS', 'COMPLETED', 'SKIPPED', 'CANCELLED');

-- CreateEnum
CREATE TYPE "PatientArrivalStatus" AS ENUM ('EXPECTED', 'ARRIVED', 'CHECKED_IN', 'WAITING', 'IN_CONSULTATION', 'COMPLETED', 'NO_SHOW', 'CANCELLED');

-- CreateEnum
CREATE TYPE "TriageCategory" AS ENUM ('ROUTINE', 'PRIORITY', 'URGENT', 'EMERGENCY');

-- CreateEnum
CREATE TYPE "EmergencyCaseStatus" AS ENUM ('ACTIVE', 'RESOURCE_HELD', 'ADMITTED', 'RESOLVED', 'CANCELLED');

-- CreateEnum
CREATE TYPE "ResourceHoldStatus" AS ENUM ('ACTIVE', 'CONFIRMED', 'EXPIRED', 'CANCELLED', 'RELEASED');

-- CreateEnum
CREATE TYPE "AIConversationMode" AS ENUM ('TEXT', 'VOICE');

-- CreateEnum
CREATE TYPE "AIConversationStatus" AS ENUM ('ACTIVE', 'COMPLETED', 'ABANDONED', 'TRIAGED');

-- CreateEnum
CREATE TYPE "CCTVOccupancyStatus" AS ENUM ('AVAILABLE', 'OCCUPIED', 'UNKNOWN', 'BLOCKED');

-- CreateEnum
CREATE TYPE "NotificationType" AS ENUM ('APPOINTMENT_CREATED', 'APPOINTMENT_UPDATED', 'APPOINTMENT_CANCELLED', 'PATIENT_ARRIVED', 'QUEUE_UPDATED', 'EMERGENCY_ALERT', 'RESOURCE_CHANGED', 'BED_AVAILABLE', 'RESOURCE_HOLD_CREATED', 'RESOURCE_HOLD_EXPIRED', 'CCTV_DISCREPANCY', 'SYSTEM_ALERT', 'TRIAGE_COMPLETED', 'OPD_SLOT_FULL');

-- CreateEnum
CREATE TYPE "NotificationChannel" AS ENUM ('IN_APP', 'WEBSOCKET', 'EMAIL', 'SMS', 'WHATSAPP');

-- CreateEnum
CREATE TYPE "NotificationStatus" AS ENUM ('PENDING', 'SENT', 'READ', 'FAILED');

-- CreateEnum
CREATE TYPE "LocationVerificationStatus" AS ENUM ('SYNTHETIC', 'UNVERIFIED', 'VERIFIED', 'DISPUTED');

-- CreateEnum
CREATE TYPE "StaffStatus" AS ENUM ('ACTIVE', 'INACTIVE', 'ON_LEAVE', 'SUSPENDED');

-- CreateTable
CREATE TABLE "states" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "code" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "states_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "districts" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "code" TEXT,
    "stateId" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "districts_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "cities" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "districtId" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "cities_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "users" (
    "id" TEXT NOT NULL,
    "demoUsername" TEXT NOT NULL,
    "displayName" TEXT NOT NULL,
    "role" "UserRole" NOT NULL,
    "hospitalId" TEXT,
    "departmentId" TEXT,
    "districtId" TEXT,
    "isActive" BOOLEAN NOT NULL DEFAULT true,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "users_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "demo_sessions" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "token" TEXT NOT NULL,
    "role" "UserRole" NOT NULL,
    "hospitalId" TEXT,
    "departmentId" TEXT,
    "districtId" TEXT,
    "permissions" TEXT[],
    "expiresAt" TIMESTAMP(3) NOT NULL,
    "isActive" BOOLEAN NOT NULL DEFAULT true,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "demo_sessions_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "patient_profiles" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "patientCode" TEXT NOT NULL,
    "firstName" TEXT NOT NULL,
    "lastName" TEXT NOT NULL,
    "dateOfBirth" TIMESTAMP(3),
    "gender" TEXT,
    "bloodGroup" TEXT,
    "phoneNumber" TEXT,
    "emergencyContact" TEXT,
    "address" TEXT,
    "city" TEXT,
    "district" TEXT,
    "state" TEXT,
    "pincode" TEXT,
    "deletedAt" TIMESTAMP(3),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "patient_profiles_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "hospitals" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "shortName" TEXT,
    "hospitalCode" TEXT NOT NULL,
    "type" TEXT NOT NULL DEFAULT 'GOVERNMENT',
    "status" "HospitalStatus" NOT NULL DEFAULT 'ACTIVE',
    "hasEmergencyDepartment" BOOLEAN NOT NULL DEFAULT false,
    "emergencyContact" TEXT,
    "generalContact" TEXT,
    "email" TEXT,
    "website" TEXT,
    "latitude" DOUBLE PRECISION,
    "longitude" DOUBLE PRECISION,
    "address" TEXT,
    "cityId" TEXT,
    "districtId" TEXT,
    "stateId" TEXT,
    "locationSource" TEXT DEFAULT 'SYNTHETIC',
    "locationVerified" "LocationVerificationStatus" NOT NULL DEFAULT 'SYNTHETIC',
    "notes" TEXT,
    "isSyntheticDemo" BOOLEAN NOT NULL DEFAULT true,
    "deletedAt" TIMESTAMP(3),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "hospitals_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "departments" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "code" TEXT NOT NULL,
    "hospitalId" TEXT NOT NULL,
    "status" "DepartmentStatus" NOT NULL DEFAULT 'ACTIVE',
    "description" TEXT,
    "floorNumber" TEXT,
    "contactExt" TEXT,
    "deletedAt" TIMESTAMP(3),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "departments_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "doctor_profiles" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "employeeCode" TEXT NOT NULL,
    "qualification" TEXT,
    "specialization" TEXT,
    "licenseNumber" TEXT,
    "hospitalId" TEXT,
    "departmentId" TEXT,
    "status" "StaffStatus" NOT NULL DEFAULT 'ACTIVE',
    "avgConsultationMinutes" INTEGER NOT NULL DEFAULT 10,
    "deletedAt" TIMESTAMP(3),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "doctor_profiles_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "nurse_profiles" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "employeeCode" TEXT NOT NULL,
    "qualification" TEXT,
    "hospitalId" TEXT,
    "departmentId" TEXT,
    "status" "StaffStatus" NOT NULL DEFAULT 'ACTIVE',
    "deletedAt" TIMESTAMP(3),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "nurse_profiles_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "reception_profiles" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "employeeCode" TEXT NOT NULL,
    "hospitalId" TEXT,
    "departmentId" TEXT,
    "status" "StaffStatus" NOT NULL DEFAULT 'ACTIVE',
    "deletedAt" TIMESTAMP(3),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "reception_profiles_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "opd_slots" (
    "id" TEXT NOT NULL,
    "hospitalId" TEXT NOT NULL,
    "departmentId" TEXT NOT NULL,
    "doctorId" TEXT,
    "date" DATE NOT NULL,
    "startTime" TEXT NOT NULL,
    "endTime" TEXT NOT NULL,
    "capacity" INTEGER NOT NULL DEFAULT 20,
    "bookedCount" INTEGER NOT NULL DEFAULT 0,
    "status" "OPDSlotStatus" NOT NULL DEFAULT 'OPEN',
    "slotCode" TEXT NOT NULL,
    "deletedAt" TIMESTAMP(3),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "opd_slots_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "appointments" (
    "id" TEXT NOT NULL,
    "appointmentCode" TEXT NOT NULL,
    "patientId" TEXT NOT NULL,
    "hospitalId" TEXT NOT NULL,
    "departmentId" TEXT NOT NULL,
    "doctorId" TEXT,
    "slotId" TEXT,
    "status" "AppointmentStatus" NOT NULL DEFAULT 'BOOKED',
    "appointmentDate" TIMESTAMP(3) NOT NULL,
    "reason" TEXT,
    "notes" TEXT,
    "source" TEXT NOT NULL DEFAULT 'ONLINE',
    "deletedAt" TIMESTAMP(3),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "appointments_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "opd_tokens" (
    "id" TEXT NOT NULL,
    "appointmentId" TEXT NOT NULL,
    "tokenNumber" INTEGER NOT NULL,
    "displayCode" TEXT NOT NULL,
    "status" "TokenStatus" NOT NULL DEFAULT 'GENERATED',
    "estimatedWaitMinutes" INTEGER,
    "calledAt" TIMESTAMP(3),
    "completedAt" TIMESTAMP(3),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "opd_tokens_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "patient_arrivals" (
    "id" TEXT NOT NULL,
    "appointmentId" TEXT NOT NULL,
    "status" "PatientArrivalStatus" NOT NULL DEFAULT 'EXPECTED',
    "arrivedAt" TIMESTAMP(3),
    "checkedInAt" TIMESTAMP(3),
    "markedBy" TEXT,
    "isOfflineArrival" BOOLEAN NOT NULL DEFAULT false,
    "notes" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "patient_arrivals_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "consultations" (
    "id" TEXT NOT NULL,
    "appointmentId" TEXT NOT NULL,
    "doctorId" TEXT NOT NULL,
    "startedAt" TIMESTAMP(3),
    "completedAt" TIMESTAMP(3),
    "durationMinutes" INTEGER,
    "diagnosis" TEXT,
    "prescription" TEXT,
    "followUpDate" TIMESTAMP(3),
    "notes" TEXT,
    "status" TEXT NOT NULL DEFAULT 'PENDING',
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "consultations_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "triage_assessments" (
    "id" TEXT NOT NULL,
    "patientId" TEXT NOT NULL,
    "conversationId" TEXT,
    "category" "TriageCategory" NOT NULL,
    "confidence" DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    "symptoms" JSONB NOT NULL,
    "primarySymptom" TEXT,
    "recommendedDepartment" TEXT,
    "safetySignals" JSONB,
    "rawAIOutput" JSONB,
    "isAIMock" BOOLEAN NOT NULL DEFAULT true,
    "modelVersion" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "triage_assessments_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "beds" (
    "id" TEXT NOT NULL,
    "bedCode" TEXT NOT NULL,
    "hospitalId" TEXT NOT NULL,
    "wardName" TEXT,
    "floorNumber" TEXT,
    "bedType" "BedType" NOT NULL DEFAULT 'GENERAL_BED',
    "status" "BedStatus" NOT NULL DEFAULT 'AVAILABLE',
    "isSyntheticDemo" BOOLEAN NOT NULL DEFAULT true,
    "notes" TEXT,
    "deletedAt" TIMESTAMP(3),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "beds_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "bed_status_history" (
    "id" TEXT NOT NULL,
    "bedId" TEXT NOT NULL,
    "oldStatus" "BedStatus" NOT NULL,
    "newStatus" "BedStatus" NOT NULL,
    "changedBy" TEXT,
    "reason" TEXT,
    "source" TEXT NOT NULL DEFAULT 'MANUAL',
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "bed_status_history_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "hospital_resources" (
    "id" TEXT NOT NULL,
    "resourceCode" TEXT NOT NULL,
    "hospitalId" TEXT NOT NULL,
    "resourceType" "ResourceType" NOT NULL,
    "status" "ResourceStatus" NOT NULL DEFAULT 'AVAILABLE',
    "totalCount" INTEGER NOT NULL DEFAULT 1,
    "availableCount" INTEGER NOT NULL DEFAULT 1,
    "notes" TEXT,
    "isSyntheticDemo" BOOLEAN NOT NULL DEFAULT true,
    "deletedAt" TIMESTAMP(3),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "hospital_resources_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "resource_status_history" (
    "id" TEXT NOT NULL,
    "resourceId" TEXT NOT NULL,
    "oldStatus" "ResourceStatus" NOT NULL,
    "newStatus" "ResourceStatus" NOT NULL,
    "changedBy" TEXT,
    "reason" TEXT,
    "source" TEXT NOT NULL DEFAULT 'MANUAL',
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "resource_status_history_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "emergency_cases" (
    "id" TEXT NOT NULL,
    "caseCode" TEXT NOT NULL,
    "patientId" TEXT NOT NULL,
    "triageId" TEXT,
    "hospitalId" TEXT,
    "status" "EmergencyCaseStatus" NOT NULL DEFAULT 'ACTIVE',
    "symptoms" JSONB,
    "patientLatitude" DOUBLE PRECISION,
    "patientLongitude" DOUBLE PRECISION,
    "notes" TEXT,
    "resolvedAt" TIMESTAMP(3),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "emergency_cases_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "emergency_routings" (
    "id" TEXT NOT NULL,
    "emergencyCaseId" TEXT NOT NULL,
    "hospitalId" TEXT NOT NULL,
    "distanceKm" DOUBLE PRECISION,
    "estimatedMinutes" DOUBLE PRECISION,
    "routingScore" DOUBLE PRECISION,
    "reasons" TEXT[],
    "isSelected" BOOLEAN NOT NULL DEFAULT false,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "emergency_routings_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "resource_holds" (
    "id" TEXT NOT NULL,
    "holdCode" TEXT NOT NULL,
    "emergencyCaseId" TEXT NOT NULL,
    "resourceId" TEXT,
    "bedId" TEXT,
    "status" "ResourceHoldStatus" NOT NULL DEFAULT 'ACTIVE',
    "expiresAt" TIMESTAMP(3) NOT NULL,
    "confirmedAt" TIMESTAMP(3),
    "releasedAt" TIMESTAMP(3),
    "notes" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "resource_holds_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "ai_conversations" (
    "id" TEXT NOT NULL,
    "patientId" TEXT NOT NULL,
    "mode" "AIConversationMode" NOT NULL DEFAULT 'TEXT',
    "language" TEXT NOT NULL DEFAULT 'en',
    "status" "AIConversationStatus" NOT NULL DEFAULT 'ACTIVE',
    "isAIMock" BOOLEAN NOT NULL DEFAULT true,
    "modelVersion" TEXT,
    "triageCategory" "TriageCategory",
    "startedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "completedAt" TIMESTAMP(3),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "ai_conversations_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "ai_messages" (
    "id" TEXT NOT NULL,
    "conversationId" TEXT NOT NULL,
    "role" TEXT NOT NULL,
    "content" TEXT NOT NULL,
    "audioUrl" TEXT,
    "language" TEXT,
    "detectedLanguage" TEXT,
    "metadata" JSONB,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "ai_messages_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "patient_state_snapshots" (
    "id" TEXT NOT NULL,
    "conversationId" TEXT NOT NULL,
    "turnNumber" INTEGER NOT NULL,
    "language" TEXT,
    "modality" TEXT,
    "symptoms" JSONB,
    "bodyLocations" JSONB,
    "onset" TEXT,
    "duration" TEXT,
    "severity" TEXT,
    "progression" TEXT,
    "frequency" TEXT,
    "associatedSymptoms" JSONB,
    "negations" JSONB,
    "vitals" JSONB,
    "history" JSONB,
    "medications" JSONB,
    "allergies" JSONB,
    "missingInfo" JSONB,
    "safetySignals" JSONB,
    "triageCategory" "TriageCategory",
    "triageConfidence" DOUBLE PRECISION,
    "modelVersions" JSONB,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "patient_state_snapshots_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "cctv_devices" (
    "id" TEXT NOT NULL,
    "deviceCode" TEXT NOT NULL,
    "hospitalId" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "location" TEXT,
    "ipAddress" TEXT,
    "isActive" BOOLEAN NOT NULL DEFAULT true,
    "isMock" BOOLEAN NOT NULL DEFAULT true,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "cctv_devices_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "cctv_zones" (
    "id" TEXT NOT NULL,
    "zoneCode" TEXT NOT NULL,
    "deviceId" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "description" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "cctv_zones_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "bed_camera_mappings" (
    "id" TEXT NOT NULL,
    "bedId" TEXT NOT NULL,
    "zoneId" TEXT NOT NULL,
    "isActive" BOOLEAN NOT NULL DEFAULT true,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "bed_camera_mappings_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "cctv_occupancy_events" (
    "id" TEXT NOT NULL,
    "deviceId" TEXT NOT NULL,
    "zoneId" TEXT,
    "bedId" TEXT,
    "occupancy" "CCTVOccupancyStatus" NOT NULL,
    "confidence" DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    "isProcessed" BOOLEAN NOT NULL DEFAULT false,
    "isMock" BOOLEAN NOT NULL DEFAULT true,
    "receivedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "cctv_occupancy_events_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "cctv_discrepancies" (
    "id" TEXT NOT NULL,
    "eventId" TEXT NOT NULL,
    "bedCode" TEXT NOT NULL,
    "cctvStatus" "CCTVOccupancyStatus" NOT NULL,
    "authoritativeStatus" "BedStatus" NOT NULL,
    "confidence" DOUBLE PRECISION NOT NULL,
    "isResolved" BOOLEAN NOT NULL DEFAULT false,
    "resolvedBy" TEXT,
    "resolvedAt" TIMESTAMP(3),
    "resolution" TEXT,
    "notes" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "cctv_discrepancies_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "notifications" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "type" "NotificationType" NOT NULL,
    "title" TEXT NOT NULL,
    "body" TEXT NOT NULL,
    "data" JSONB,
    "status" "NotificationStatus" NOT NULL DEFAULT 'PENDING',
    "channel" "NotificationChannel" NOT NULL DEFAULT 'IN_APP',
    "readAt" TIMESTAMP(3),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "notifications_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "audit_logs" (
    "id" TEXT NOT NULL,
    "actorId" TEXT,
    "actorRole" TEXT,
    "action" TEXT NOT NULL,
    "entity" TEXT NOT NULL,
    "entityId" TEXT,
    "oldValue" JSONB,
    "newValue" JSONB,
    "reason" TEXT,
    "requestId" TEXT,
    "ipAddress" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "audit_logs_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "analytics_snapshots" (
    "id" TEXT NOT NULL,
    "hospitalId" TEXT,
    "districtId" TEXT,
    "stateId" TEXT,
    "snapshotDate" DATE NOT NULL,
    "snapshotHour" INTEGER,
    "data" JSONB NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "analytics_snapshots_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "location_requests" (
    "id" TEXT NOT NULL,
    "patientId" TEXT,
    "latitude" DOUBLE PRECISION,
    "longitude" DOUBLE PRECISION,
    "accuracy" DOUBLE PRECISION,
    "address" TEXT,
    "isManual" BOOLEAN NOT NULL DEFAULT false,
    "sessionRef" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "location_requests_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "geocoding_cache" (
    "id" TEXT NOT NULL,
    "query" TEXT NOT NULL,
    "result" JSONB NOT NULL,
    "provider" TEXT NOT NULL DEFAULT 'nominatim',
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "expiresAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "geocoding_cache_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "system_events" (
    "id" TEXT NOT NULL,
    "eventType" TEXT NOT NULL,
    "payload" JSONB,
    "source" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "system_events_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "states_name_key" ON "states"("name");

-- CreateIndex
CREATE UNIQUE INDEX "states_code_key" ON "states"("code");

-- CreateIndex
CREATE UNIQUE INDEX "districts_name_stateId_key" ON "districts"("name", "stateId");

-- CreateIndex
CREATE UNIQUE INDEX "cities_name_districtId_key" ON "cities"("name", "districtId");

-- CreateIndex
CREATE UNIQUE INDEX "users_demoUsername_key" ON "users"("demoUsername");

-- CreateIndex
CREATE UNIQUE INDEX "demo_sessions_token_key" ON "demo_sessions"("token");

-- CreateIndex
CREATE INDEX "demo_sessions_token_idx" ON "demo_sessions"("token");

-- CreateIndex
CREATE UNIQUE INDEX "patient_profiles_userId_key" ON "patient_profiles"("userId");

-- CreateIndex
CREATE UNIQUE INDEX "patient_profiles_patientCode_key" ON "patient_profiles"("patientCode");

-- CreateIndex
CREATE UNIQUE INDEX "hospitals_hospitalCode_key" ON "hospitals"("hospitalCode");

-- CreateIndex
CREATE INDEX "hospitals_latitude_longitude_idx" ON "hospitals"("latitude", "longitude");

-- CreateIndex
CREATE INDEX "hospitals_districtId_idx" ON "hospitals"("districtId");

-- CreateIndex
CREATE UNIQUE INDEX "departments_code_hospitalId_key" ON "departments"("code", "hospitalId");

-- CreateIndex
CREATE UNIQUE INDEX "doctor_profiles_userId_key" ON "doctor_profiles"("userId");

-- CreateIndex
CREATE UNIQUE INDEX "doctor_profiles_employeeCode_key" ON "doctor_profiles"("employeeCode");

-- CreateIndex
CREATE UNIQUE INDEX "nurse_profiles_userId_key" ON "nurse_profiles"("userId");

-- CreateIndex
CREATE UNIQUE INDEX "nurse_profiles_employeeCode_key" ON "nurse_profiles"("employeeCode");

-- CreateIndex
CREATE UNIQUE INDEX "reception_profiles_userId_key" ON "reception_profiles"("userId");

-- CreateIndex
CREATE UNIQUE INDEX "reception_profiles_employeeCode_key" ON "reception_profiles"("employeeCode");

-- CreateIndex
CREATE UNIQUE INDEX "opd_slots_slotCode_key" ON "opd_slots"("slotCode");

-- CreateIndex
CREATE INDEX "opd_slots_hospitalId_date_status_idx" ON "opd_slots"("hospitalId", "date", "status");

-- CreateIndex
CREATE INDEX "opd_slots_departmentId_date_status_idx" ON "opd_slots"("departmentId", "date", "status");

-- CreateIndex
CREATE UNIQUE INDEX "appointments_appointmentCode_key" ON "appointments"("appointmentCode");

-- CreateIndex
CREATE INDEX "appointments_patientId_status_idx" ON "appointments"("patientId", "status");

-- CreateIndex
CREATE INDEX "appointments_hospitalId_appointmentDate_idx" ON "appointments"("hospitalId", "appointmentDate");

-- CreateIndex
CREATE UNIQUE INDEX "opd_tokens_appointmentId_key" ON "opd_tokens"("appointmentId");

-- CreateIndex
CREATE UNIQUE INDEX "patient_arrivals_appointmentId_key" ON "patient_arrivals"("appointmentId");

-- CreateIndex
CREATE UNIQUE INDEX "consultations_appointmentId_key" ON "consultations"("appointmentId");

-- CreateIndex
CREATE UNIQUE INDEX "beds_bedCode_key" ON "beds"("bedCode");

-- CreateIndex
CREATE INDEX "beds_hospitalId_status_bedType_idx" ON "beds"("hospitalId", "status", "bedType");

-- CreateIndex
CREATE INDEX "bed_status_history_bedId_idx" ON "bed_status_history"("bedId");

-- CreateIndex
CREATE UNIQUE INDEX "hospital_resources_resourceCode_key" ON "hospital_resources"("resourceCode");

-- CreateIndex
CREATE INDEX "hospital_resources_hospitalId_resourceType_status_idx" ON "hospital_resources"("hospitalId", "resourceType", "status");

-- CreateIndex
CREATE INDEX "resource_status_history_resourceId_idx" ON "resource_status_history"("resourceId");

-- CreateIndex
CREATE UNIQUE INDEX "emergency_cases_caseCode_key" ON "emergency_cases"("caseCode");

-- CreateIndex
CREATE INDEX "emergency_cases_status_idx" ON "emergency_cases"("status");

-- CreateIndex
CREATE UNIQUE INDEX "resource_holds_holdCode_key" ON "resource_holds"("holdCode");

-- CreateIndex
CREATE INDEX "resource_holds_status_expiresAt_idx" ON "resource_holds"("status", "expiresAt");

-- CreateIndex
CREATE INDEX "ai_conversations_patientId_status_idx" ON "ai_conversations"("patientId", "status");

-- CreateIndex
CREATE INDEX "ai_messages_conversationId_idx" ON "ai_messages"("conversationId");

-- CreateIndex
CREATE INDEX "patient_state_snapshots_conversationId_turnNumber_idx" ON "patient_state_snapshots"("conversationId", "turnNumber");

-- CreateIndex
CREATE UNIQUE INDEX "cctv_devices_deviceCode_key" ON "cctv_devices"("deviceCode");

-- CreateIndex
CREATE UNIQUE INDEX "cctv_zones_zoneCode_key" ON "cctv_zones"("zoneCode");

-- CreateIndex
CREATE UNIQUE INDEX "bed_camera_mappings_bedId_zoneId_key" ON "bed_camera_mappings"("bedId", "zoneId");

-- CreateIndex
CREATE INDEX "cctv_occupancy_events_deviceId_isProcessed_idx" ON "cctv_occupancy_events"("deviceId", "isProcessed");

-- CreateIndex
CREATE UNIQUE INDEX "cctv_discrepancies_eventId_key" ON "cctv_discrepancies"("eventId");

-- CreateIndex
CREATE INDEX "cctv_discrepancies_isResolved_idx" ON "cctv_discrepancies"("isResolved");

-- CreateIndex
CREATE INDEX "notifications_userId_status_idx" ON "notifications"("userId", "status");

-- CreateIndex
CREATE INDEX "audit_logs_entity_entityId_idx" ON "audit_logs"("entity", "entityId");

-- CreateIndex
CREATE INDEX "audit_logs_actorId_idx" ON "audit_logs"("actorId");

-- CreateIndex
CREATE INDEX "audit_logs_createdAt_idx" ON "audit_logs"("createdAt");

-- CreateIndex
CREATE INDEX "analytics_snapshots_hospitalId_snapshotDate_idx" ON "analytics_snapshots"("hospitalId", "snapshotDate");

-- CreateIndex
CREATE INDEX "analytics_snapshots_districtId_snapshotDate_idx" ON "analytics_snapshots"("districtId", "snapshotDate");

-- CreateIndex
CREATE UNIQUE INDEX "geocoding_cache_query_key" ON "geocoding_cache"("query");

-- CreateIndex
CREATE INDEX "geocoding_cache_query_idx" ON "geocoding_cache"("query");

-- CreateIndex
CREATE INDEX "system_events_eventType_idx" ON "system_events"("eventType");

-- AddForeignKey
ALTER TABLE "districts" ADD CONSTRAINT "districts_stateId_fkey" FOREIGN KEY ("stateId") REFERENCES "states"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "cities" ADD CONSTRAINT "cities_districtId_fkey" FOREIGN KEY ("districtId") REFERENCES "districts"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "users" ADD CONSTRAINT "users_hospitalId_fkey" FOREIGN KEY ("hospitalId") REFERENCES "hospitals"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "users" ADD CONSTRAINT "users_departmentId_fkey" FOREIGN KEY ("departmentId") REFERENCES "departments"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "users" ADD CONSTRAINT "users_districtId_fkey" FOREIGN KEY ("districtId") REFERENCES "districts"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "demo_sessions" ADD CONSTRAINT "demo_sessions_userId_fkey" FOREIGN KEY ("userId") REFERENCES "users"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "patient_profiles" ADD CONSTRAINT "patient_profiles_userId_fkey" FOREIGN KEY ("userId") REFERENCES "users"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "hospitals" ADD CONSTRAINT "hospitals_cityId_fkey" FOREIGN KEY ("cityId") REFERENCES "cities"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "hospitals" ADD CONSTRAINT "hospitals_districtId_fkey" FOREIGN KEY ("districtId") REFERENCES "districts"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "hospitals" ADD CONSTRAINT "hospitals_stateId_fkey" FOREIGN KEY ("stateId") REFERENCES "states"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "departments" ADD CONSTRAINT "departments_hospitalId_fkey" FOREIGN KEY ("hospitalId") REFERENCES "hospitals"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "doctor_profiles" ADD CONSTRAINT "doctor_profiles_userId_fkey" FOREIGN KEY ("userId") REFERENCES "users"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "doctor_profiles" ADD CONSTRAINT "doctor_profiles_departmentId_fkey" FOREIGN KEY ("departmentId") REFERENCES "departments"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "nurse_profiles" ADD CONSTRAINT "nurse_profiles_userId_fkey" FOREIGN KEY ("userId") REFERENCES "users"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "nurse_profiles" ADD CONSTRAINT "nurse_profiles_departmentId_fkey" FOREIGN KEY ("departmentId") REFERENCES "departments"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "reception_profiles" ADD CONSTRAINT "reception_profiles_userId_fkey" FOREIGN KEY ("userId") REFERENCES "users"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "reception_profiles" ADD CONSTRAINT "reception_profiles_departmentId_fkey" FOREIGN KEY ("departmentId") REFERENCES "departments"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "opd_slots" ADD CONSTRAINT "opd_slots_hospitalId_fkey" FOREIGN KEY ("hospitalId") REFERENCES "hospitals"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "opd_slots" ADD CONSTRAINT "opd_slots_departmentId_fkey" FOREIGN KEY ("departmentId") REFERENCES "departments"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "opd_slots" ADD CONSTRAINT "opd_slots_doctorId_fkey" FOREIGN KEY ("doctorId") REFERENCES "doctor_profiles"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "appointments" ADD CONSTRAINT "appointments_patientId_fkey" FOREIGN KEY ("patientId") REFERENCES "patient_profiles"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "appointments" ADD CONSTRAINT "appointments_hospitalId_fkey" FOREIGN KEY ("hospitalId") REFERENCES "hospitals"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "appointments" ADD CONSTRAINT "appointments_departmentId_fkey" FOREIGN KEY ("departmentId") REFERENCES "departments"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "appointments" ADD CONSTRAINT "appointments_doctorId_fkey" FOREIGN KEY ("doctorId") REFERENCES "doctor_profiles"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "appointments" ADD CONSTRAINT "appointments_slotId_fkey" FOREIGN KEY ("slotId") REFERENCES "opd_slots"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "opd_tokens" ADD CONSTRAINT "opd_tokens_appointmentId_fkey" FOREIGN KEY ("appointmentId") REFERENCES "appointments"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "patient_arrivals" ADD CONSTRAINT "patient_arrivals_appointmentId_fkey" FOREIGN KEY ("appointmentId") REFERENCES "appointments"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "patient_arrivals" ADD CONSTRAINT "patient_arrivals_markedBy_fkey" FOREIGN KEY ("markedBy") REFERENCES "reception_profiles"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "consultations" ADD CONSTRAINT "consultations_appointmentId_fkey" FOREIGN KEY ("appointmentId") REFERENCES "appointments"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "consultations" ADD CONSTRAINT "consultations_doctorId_fkey" FOREIGN KEY ("doctorId") REFERENCES "doctor_profiles"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "triage_assessments" ADD CONSTRAINT "triage_assessments_patientId_fkey" FOREIGN KEY ("patientId") REFERENCES "patient_profiles"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "triage_assessments" ADD CONSTRAINT "triage_assessments_conversationId_fkey" FOREIGN KEY ("conversationId") REFERENCES "ai_conversations"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "beds" ADD CONSTRAINT "beds_hospitalId_fkey" FOREIGN KEY ("hospitalId") REFERENCES "hospitals"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "bed_status_history" ADD CONSTRAINT "bed_status_history_bedId_fkey" FOREIGN KEY ("bedId") REFERENCES "beds"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "hospital_resources" ADD CONSTRAINT "hospital_resources_hospitalId_fkey" FOREIGN KEY ("hospitalId") REFERENCES "hospitals"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "resource_status_history" ADD CONSTRAINT "resource_status_history_resourceId_fkey" FOREIGN KEY ("resourceId") REFERENCES "hospital_resources"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "emergency_cases" ADD CONSTRAINT "emergency_cases_patientId_fkey" FOREIGN KEY ("patientId") REFERENCES "patient_profiles"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "emergency_cases" ADD CONSTRAINT "emergency_cases_triageId_fkey" FOREIGN KEY ("triageId") REFERENCES "triage_assessments"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "emergency_cases" ADD CONSTRAINT "emergency_cases_hospitalId_fkey" FOREIGN KEY ("hospitalId") REFERENCES "hospitals"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "emergency_routings" ADD CONSTRAINT "emergency_routings_emergencyCaseId_fkey" FOREIGN KEY ("emergencyCaseId") REFERENCES "emergency_cases"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "emergency_routings" ADD CONSTRAINT "emergency_routings_hospitalId_fkey" FOREIGN KEY ("hospitalId") REFERENCES "hospitals"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "resource_holds" ADD CONSTRAINT "resource_holds_emergencyCaseId_fkey" FOREIGN KEY ("emergencyCaseId") REFERENCES "emergency_cases"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "resource_holds" ADD CONSTRAINT "resource_holds_resourceId_fkey" FOREIGN KEY ("resourceId") REFERENCES "hospital_resources"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "resource_holds" ADD CONSTRAINT "resource_holds_bedId_fkey" FOREIGN KEY ("bedId") REFERENCES "beds"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ai_conversations" ADD CONSTRAINT "ai_conversations_patientId_fkey" FOREIGN KEY ("patientId") REFERENCES "patient_profiles"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ai_messages" ADD CONSTRAINT "ai_messages_conversationId_fkey" FOREIGN KEY ("conversationId") REFERENCES "ai_conversations"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "patient_state_snapshots" ADD CONSTRAINT "patient_state_snapshots_conversationId_fkey" FOREIGN KEY ("conversationId") REFERENCES "ai_conversations"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "cctv_devices" ADD CONSTRAINT "cctv_devices_hospitalId_fkey" FOREIGN KEY ("hospitalId") REFERENCES "hospitals"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "cctv_zones" ADD CONSTRAINT "cctv_zones_deviceId_fkey" FOREIGN KEY ("deviceId") REFERENCES "cctv_devices"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "bed_camera_mappings" ADD CONSTRAINT "bed_camera_mappings_bedId_fkey" FOREIGN KEY ("bedId") REFERENCES "beds"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "bed_camera_mappings" ADD CONSTRAINT "bed_camera_mappings_zoneId_fkey" FOREIGN KEY ("zoneId") REFERENCES "cctv_zones"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "cctv_occupancy_events" ADD CONSTRAINT "cctv_occupancy_events_deviceId_fkey" FOREIGN KEY ("deviceId") REFERENCES "cctv_devices"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "cctv_occupancy_events" ADD CONSTRAINT "cctv_occupancy_events_zoneId_fkey" FOREIGN KEY ("zoneId") REFERENCES "cctv_zones"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "cctv_discrepancies" ADD CONSTRAINT "cctv_discrepancies_eventId_fkey" FOREIGN KEY ("eventId") REFERENCES "cctv_occupancy_events"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "notifications" ADD CONSTRAINT "notifications_userId_fkey" FOREIGN KEY ("userId") REFERENCES "users"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "audit_logs" ADD CONSTRAINT "audit_logs_actorId_fkey" FOREIGN KEY ("actorId") REFERENCES "users"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "analytics_snapshots" ADD CONSTRAINT "analytics_snapshots_hospitalId_fkey" FOREIGN KEY ("hospitalId") REFERENCES "hospitals"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "location_requests" ADD CONSTRAINT "location_requests_patientId_fkey" FOREIGN KEY ("patientId") REFERENCES "patient_profiles"("id") ON DELETE SET NULL ON UPDATE CASCADE;
