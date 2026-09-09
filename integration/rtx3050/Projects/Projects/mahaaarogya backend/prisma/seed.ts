/**
 * MahaArogya — Sanjeevani Grid
 * Complete Database Seed
 *
 * Creates:
 * - Maharashtra state + Nagpur district + cities
 * - 5 synthetic hospitals in Nagpur area
 * - Departments, doctors, nurses, reception
 * - Beds (general + ICU), oxygen resources
 * - OPD slots
 * - Demo users for all 9 roles
 * - CCTV devices (mock)
 *
 * All data is SYNTHETIC / DEMO only.
 */

import { PrismaClient, UserRole, BedType, BedStatus, OPDSlotStatus, ResourceType, ResourceStatus } from '@prisma/client';
import { v4 as uuidv4 } from 'uuid';
import * as bcrypt from 'bcrypt';

const prisma = new PrismaClient();

// Helper
const uid = () => uuidv4();
const today = new Date();
const tomorrow = new Date(today);
tomorrow.setDate(tomorrow.getDate() + 1);

function makeDate(daysOffset: number): Date {
  const d = new Date();
  d.setDate(d.getDate() + daysOffset);
  d.setHours(0, 0, 0, 0);
  return d;
}

async function main() {
  console.log('🌱 Starting MahaArogya database seed...');

  // ── Step 1: State + District + Cities ───────────────────────
  console.log('📍 Creating geography...');
  const stateId = uid();
  await prisma.state.upsert({
    where: { code: 'MH' },
    create: { id: stateId, name: 'Maharashtra', code: 'MH' },
    update: {},
  });
  const state = await prisma.state.findUnique({ where: { code: 'MH' } });

  const districtId = uid();
  let district = await prisma.district.findFirst({ where: { name: 'Nagpur', stateId: state!.id } });
  if (!district) {
    district = await prisma.district.create({
      data: { id: districtId, name: 'Nagpur', code: 'NGP', stateId: state!.id },
    });
  }

  const cityNames = ['Nagpur', 'Kamptee', 'Hingna', 'Butibori', 'Wardha Road'];
  const cities: Record<string, { id: string }> = {};
  for (const cityName of cityNames) {
    let city = await prisma.city.findFirst({ where: { name: cityName, districtId: district.id } });
    if (!city) {
      city = await prisma.city.create({
        data: { id: uid(), name: cityName, districtId: district.id },
      });
    }
    cities[cityName] = city;
  }
  console.log('✅ Geography created');

  // ── Step 2: Hospitals ────────────────────────────────────────
  console.log('🏥 Creating hospitals...');

  const hospitalData = [
    {
      id: uid(),
      name: 'Government Medical College & Hospital Nagpur',
      shortName: 'GMCH Nagpur',
      hospitalCode: 'GMCH-NGP-001',
      type: 'GOVERNMENT',
      hasEmergencyDepartment: true,
      emergencyContact: '0712-2700000',
      latitude: 21.1468,
      longitude: 79.0822,
      address: 'Medical Square, Nagpur, Maharashtra 440003',
      cityName: 'Nagpur',
    },
    {
      id: uid(),
      name: 'All India Institute of Medical Sciences Nagpur',
      shortName: 'AIIMS Nagpur',
      hospitalCode: 'AIIMS-NGP-001',
      type: 'GOVERNMENT',
      hasEmergencyDepartment: true,
      emergencyContact: '0712-2910000',
      latitude: 21.0890,
      longitude: 79.0521,
      address: 'Plot No 2, Sector 20, MIHAN, Nagpur 441108',
      cityName: 'Butibori',
    },
    {
      id: uid(),
      name: 'Indira Gandhi Government Medical College',
      shortName: 'IGGMC',
      hospitalCode: 'IGGMC-NGP-001',
      type: 'GOVERNMENT',
      hasEmergencyDepartment: true,
      emergencyContact: '0712-2723800',
      latitude: 21.1558,
      longitude: 79.0933,
      address: 'Central Avenue, Nagpur, Maharashtra 440018',
      cityName: 'Nagpur',
    },
    {
      id: uid(),
      name: 'Wockhardt Hospital Nagpur',
      shortName: 'Wockhardt',
      hospitalCode: 'WOCK-NGP-001',
      type: 'PRIVATE',
      hasEmergencyDepartment: true,
      emergencyContact: '0712-6682500',
      latitude: 21.1413,
      longitude: 79.0938,
      address: 'Jail Road, Nagpur 440001',
      cityName: 'Nagpur',
    },
    {
      id: uid(),
      name: 'Kamptee District Rural Hospital',
      shortName: 'Kamptee Rural',
      hospitalCode: 'KRH-NGP-001',
      type: 'GOVERNMENT',
      hasEmergencyDepartment: false,
      emergencyContact: '0712-2620100',
      latitude: 21.2223,
      longitude: 79.1968,
      address: 'Station Road, Kamptee, Nagpur 441001',
      cityName: 'Kamptee',
    },
  ];

  const hospitals: Record<string, string> = {};
  for (const h of hospitalData) {
    const cityId = cities[h.cityName]?.id;
    const existing = await prisma.hospital.findUnique({ where: { hospitalCode: h.hospitalCode } });
    if (!existing) {
      await prisma.hospital.create({
        data: {
          id: h.id,
          name: h.name,
          shortName: h.shortName,
          hospitalCode: h.hospitalCode,
          type: h.type,
          status: 'ACTIVE',
          hasEmergencyDepartment: h.hasEmergencyDepartment,
          emergencyContact: h.emergencyContact,
          latitude: h.latitude,
          longitude: h.longitude,
          address: h.address,
          cityId,
          districtId: district.id,
          stateId: state!.id,
          isSyntheticDemo: true,
        },
      });
      hospitals[h.hospitalCode] = h.id;
    } else {
      hospitals[h.hospitalCode] = existing.id;
    }
  }
  console.log('✅ Hospitals created');

  // ── Step 3: Departments ──────────────────────────────────────
  console.log('🏛️  Creating departments...');
  const deptTemplates = [
    { name: 'General Medicine', code: 'GM' },
    { name: 'Emergency', code: 'EM' },
    { name: 'Cardiology', code: 'CARD' },
    { name: 'Neurology', code: 'NEUR' },
    { name: 'Orthopedics', code: 'ORTH' },
    { name: 'Pediatrics', code: 'PED' },
    { name: 'Obstetrics & Gynecology', code: 'OBG' },
    { name: 'Pulmonology', code: 'PULM' },
  ];

  const deptIds: Record<string, string> = {};
  for (const [hCode, hId] of Object.entries(hospitals)) {
    for (const dept of deptTemplates.slice(0, hCode === 'KRH-NGP-001' ? 3 : 6)) {
      const key = `${hId}-${dept.code}`;
      const existing = await prisma.department.findUnique({
        where: { code_hospitalId: { code: dept.code, hospitalId: hId } },
      });
      if (!existing) {
        const d = await prisma.department.create({
          data: { id: uid(), name: dept.name, code: dept.code, hospitalId: hId, status: 'ACTIVE' },
        });
        deptIds[key] = d.id;
      } else {
        deptIds[key] = existing.id;
      }
    }
  }
  console.log('✅ Departments created');

  // ── Step 4: Demo Users ───────────────────────────────────────
  console.log('👤 Creating demo users...');

  const gmchId = hospitals['GMCH-NGP-001'];
  const aiimId = hospitals['AIIMS-NGP-001'];

  const demoUsers: Array<{
    username: string;
    displayName: string;
    role: UserRole;
    hospitalId?: string;
    departmentId?: string;
    districtId?: string;
  }> = [
    { username: 'demo-patient', displayName: 'Demo Patient (Rahul Sharma)', role: 'PUBLIC_PATIENT' },
    { username: 'demo-doctor', displayName: 'Dr. Priya Desai (Demo)', role: 'DOCTOR', hospitalId: gmchId, departmentId: deptIds[`${gmchId}-GM`] },
    { username: 'demo-nurse', displayName: 'Nurse Sunita Patil (Demo)', role: 'NURSE', hospitalId: gmchId },
    { username: 'demo-reception', displayName: 'Reception Staff Amit Kale (Demo)', role: 'RECEPTION', hospitalId: gmchId },
    { username: 'demo-hospital-admin', displayName: 'Hospital Admin Vikram Singh (Demo)', role: 'HOSPITAL_ADMIN', hospitalId: gmchId },
    { username: 'demo-hospital-head', displayName: 'Hospital Head Dr. Rajesh Mehta (Demo)', role: 'HOSPITAL_HEAD', hospitalId: gmchId },
    { username: 'demo-dho', displayName: 'District Health Officer Dr. Sanjay Rao (Demo)', role: 'DISTRICT_HEALTH_OFFICER', districtId: district.id },
    { username: 'demo-govt', displayName: 'Government Official Mrs. Anita Joshi (Demo)', role: 'GOVERNMENT_OFFICIAL' },
    { username: 'demo-sysadmin', displayName: 'System Admin (Demo)', role: 'SYSTEM_ADMIN' },
  ];

  const createdUsers: Record<string, string> = {};
  for (const u of demoUsers) {
    let user = await prisma.user.findUnique({ where: { demoUsername: u.username } });
    if (!user) {
      user = await prisma.user.create({
        data: {
          id: uid(),
          demoUsername: u.username,
          displayName: u.displayName,
          role: u.role,
          hospitalId: u.hospitalId || null,
          departmentId: u.departmentId || null,
          districtId: u.districtId || null,
          isActive: true,
        },
      });
    }
    createdUsers[u.username] = user.id;
  }
  console.log('✅ Demo users created');

  // ── Step 5: Patient Profile ──────────────────────────────────
  console.log('🧑‍⚕️ Creating patient profile...');
  const patientUserId = createdUsers['demo-patient'];
  const existingPatient = await prisma.patientProfile.findUnique({ where: { userId: patientUserId } });
  let patientId: string;
  if (!existingPatient) {
    const p = await prisma.patientProfile.create({
      data: {
        id: uid(),
        userId: patientUserId,
        patientCode: 'PAT-2024-00001',
        firstName: 'Rahul',
        lastName: 'Sharma',
        dateOfBirth: new Date('1990-05-15'),
        gender: 'MALE',
        bloodGroup: 'B+',
        phoneNumber: '9876543210',
        address: '45 Dharampeth, Nagpur',
        city: 'Nagpur',
        district: 'Nagpur',
        state: 'Maharashtra',
        pincode: '440010',
      },
    });
    patientId = p.id;
  } else {
    patientId = existingPatient.id;
  }
  console.log('✅ Patient profile created');

  // ── Step 6: Doctor / Nurse / Reception Profiles ──────────────
  console.log('👨‍⚕️ Creating staff profiles...');
  const doctorUserId = createdUsers['demo-doctor'];
  if (!(await prisma.doctorProfile.findUnique({ where: { userId: doctorUserId } }))) {
    await prisma.doctorProfile.create({
      data: {
        id: uid(),
        userId: doctorUserId,
        employeeCode: 'DOC-GM-001',
        qualification: 'MBBS, MD (Medicine)',
        specialization: 'General Medicine',
        licenseNumber: 'MH-DOC-123456',
        hospitalId: gmchId,
        departmentId: deptIds[`${gmchId}-GM`],
        status: 'ACTIVE',
        avgConsultationMinutes: 10,
      },
    });
  }

  const nurseUserId = createdUsers['demo-nurse'];
  if (!(await prisma.nurseProfile.findUnique({ where: { userId: nurseUserId } }))) {
    await prisma.nurseProfile.create({
      data: {
        id: uid(),
        userId: nurseUserId,
        employeeCode: 'NRS-GM-001',
        hospitalId: gmchId,
        departmentId: deptIds[`${gmchId}-GM`],
        status: 'ACTIVE',
      },
    });
  }

  const receptionUserId = createdUsers['demo-reception'];
  if (!(await prisma.receptionProfile.findUnique({ where: { userId: receptionUserId } }))) {
    await prisma.receptionProfile.create({
      data: {
        id: uid(),
        userId: receptionUserId,
        employeeCode: 'REC-001',
        hospitalId: gmchId,
        status: 'ACTIVE',
      },
    });
  }
  console.log('✅ Staff profiles created');

  // ── Step 7: Beds ─────────────────────────────────────────────
  console.log('🛏️  Creating beds...');
  for (const [hCode, hId] of Object.entries(hospitals)) {
    const isLarge = !['KRH-NGP-001'].includes(hCode);
    const generalBedCount = isLarge ? 40 : 15;
    const icuBedCount = isLarge ? 10 : 3;
    const emergencyBedCount = isLarge ? 8 : 2;

    // General beds
    for (let i = 1; i <= generalBedCount; i++) {
      const bedCode = `${hCode}-G${String(i).padStart(3, '0')}`;
      const exists = await prisma.bed.findUnique({ where: { bedCode } });
      if (!exists) {
        await prisma.bed.create({
          data: {
            id: uid(),
            bedCode,
            hospitalId: hId,
            wardName: `Ward ${Math.ceil(i / 10)}`,
            floorNumber: `${Math.ceil(i / 20)}`,
            bedType: 'GENERAL_BED',
            status: i <= Math.floor(generalBedCount * 0.6) ? 'OCCUPIED' : 'AVAILABLE',
            isSyntheticDemo: true,
          },
        });
      }
    }

    // ICU beds
    for (let i = 1; i <= icuBedCount; i++) {
      const bedCode = `${hCode}-ICU${String(i).padStart(2, '0')}`;
      const exists = await prisma.bed.findUnique({ where: { bedCode } });
      if (!exists) {
        await prisma.bed.create({
          data: {
            id: uid(),
            bedCode,
            hospitalId: hId,
            wardName: 'ICU',
            floorNumber: '3',
            bedType: 'ICU_BED',
            status: i <= Math.floor(icuBedCount * 0.7) ? 'OCCUPIED' : 'AVAILABLE',
            isSyntheticDemo: true,
          },
        });
      }
    }

    // Emergency beds
    for (let i = 1; i <= emergencyBedCount; i++) {
      const bedCode = `${hCode}-EM${String(i).padStart(2, '0')}`;
      const exists = await prisma.bed.findUnique({ where: { bedCode } });
      if (!exists) {
        await prisma.bed.create({
          data: {
            id: uid(),
            bedCode,
            hospitalId: hId,
            wardName: 'Emergency',
            floorNumber: 'G',
            bedType: 'EMERGENCY_BED',
            status: i <= 2 ? 'OCCUPIED' : 'AVAILABLE',
            isSyntheticDemo: true,
          },
        });
      }
    }
  }
  console.log('✅ Beds created');

  // ── Step 8: Hospital Resources (Oxygen, Ventilators) ─────────
  console.log('💨 Creating hospital resources...');
  for (const [hCode, hId] of Object.entries(hospitals)) {
    const isLarge = !['KRH-NGP-001'].includes(hCode);

    const resources = [
      { type: 'OXYGEN_CYLINDER' as ResourceType, total: isLarge ? 50 : 15 },
      { type: 'VENTILATOR' as ResourceType, total: isLarge ? 8 : 2 },
    ];

    for (const r of resources) {
      const resCode = `${hCode}-${r.type}-001`;
      const exists = await prisma.hospitalResource.findUnique({ where: { resourceCode: resCode } });
      if (!exists) {
        const available = Math.floor(r.total * 0.4);
        await prisma.hospitalResource.create({
          data: {
            id: uid(),
            resourceCode: resCode,
            hospitalId: hId,
            resourceType: r.type,
            status: 'AVAILABLE',
            totalCount: r.total,
            availableCount: available,
            isSyntheticDemo: true,
          },
        });
      }
    }
  }
  console.log('✅ Hospital resources created');

  // ── Step 9: OPD Slots ────────────────────────────────────────
  console.log('📅 Creating OPD slots...');
  const doctorProfile = await prisma.doctorProfile.findUnique({ where: { userId: doctorUserId } });

  for (let dayOffset = 0; dayOffset <= 7; dayOffset++) {
    const slotDate = makeDate(dayOffset);
    const timeSlots = [
      { start: '09:00', end: '09:30' },
      { start: '09:30', end: '10:00' },
      { start: '10:00', end: '10:30' },
      { start: '10:30', end: '11:00' },
      { start: '11:00', end: '11:30' },
      { start: '14:00', end: '14:30' },
      { start: '14:30', end: '15:00' },
      { start: '15:00', end: '15:30' },
    ];

    const gmDeptId = deptIds[`${gmchId}-GM`];
    if (!gmDeptId) continue;

    for (const ts of timeSlots) {
      const slotCode = `GMCH-GM-${slotDate.toISOString().split('T')[0]}-${ts.start.replace(':', '')}`;
      const exists = await prisma.oPDSlot.findUnique({ where: { slotCode } });
      if (!exists) {
        const booked = Math.floor(Math.random() * 12);
        const capacity = 20;
        const status: OPDSlotStatus =
          booked >= capacity ? 'FULL' : booked >= capacity * 0.8 ? 'NEAR_FULL' : 'OPEN';
        await prisma.oPDSlot.create({
          data: {
            id: uid(),
            hospitalId: gmchId,
            departmentId: gmDeptId,
            doctorId: doctorProfile?.id || null,
            date: slotDate,
            startTime: ts.start,
            endTime: ts.end,
            capacity,
            bookedCount: booked,
            status,
            slotCode,
          },
        });
      }
    }
  }
  console.log('✅ OPD slots created');

  // ── Step 10: CCTV Devices ────────────────────────────────────
  console.log('📷 Creating CCTV devices (mock)...');
  const cctvDeviceCode = 'MOCK-CAM-GMCH-ICU-01';
  let cctvDevice = await prisma.cCTVDevice.findUnique({ where: { deviceCode: cctvDeviceCode } });
  if (!cctvDevice) {
    cctvDevice = await prisma.cCTVDevice.create({
      data: {
        id: uid(),
        deviceCode: cctvDeviceCode,
        hospitalId: gmchId,
        name: 'ICU Camera 01 (Mock)',
        location: 'ICU Ward, Floor 3',
        isActive: true,
        isMock: true,
      },
    });
  }

  // Create zone
  let zone = await prisma.cCTVZone.findUnique({ where: { zoneCode: 'ZONE-ICU-01' } });
  if (!zone) {
    zone = await prisma.cCTVZone.create({
      data: {
        id: uid(),
        zoneCode: 'ZONE-ICU-01',
        deviceId: cctvDevice.id,
        name: 'ICU Zone A',
      },
    });
  }

  // Map ICU beds to zone
  const icuBeds = await prisma.bed.findMany({
    where: { hospitalId: gmchId, bedType: 'ICU_BED' },
    take: 3,
  });
  for (const bed of icuBeds) {
    const mapping = await prisma.bedCameraMapping.findFirst({
      where: { bedId: bed.id, zoneId: zone.id },
    });
    if (!mapping) {
      await prisma.bedCameraMapping.create({
        data: { id: uid(), bedId: bed.id, zoneId: zone.id, isActive: true },
      });
    }
  }
  console.log('✅ CCTV devices created');

  // ── Done ─────────────────────────────────────────────────────
  console.log('\n🎉 MahaArogya seed complete!\n');
  console.log('Demo login credentials:');
  console.log('────────────────────────────────────────');
  for (const u of demoUsers) {
    console.log(`  Role: ${u.role.padEnd(28)} → username: ${u.username}`);
  }
  console.log('────────────────────────────────────────');
  console.log('Use POST /api/v1/auth/demo-login with {"role": "<ROLE_NAME>"} to get token\n');
}

main()
  .catch((e) => {
    console.error('❌ Seed failed:', e);
    process.exit(1);
  })
  .finally(() => prisma.$disconnect());
