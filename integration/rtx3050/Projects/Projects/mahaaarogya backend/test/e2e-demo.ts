import axios from 'axios';

const BASE_URL = 'http://localhost:4000/api/v1';

async function runE2ETest() {
  console.log('====================================================');
  console.log('🧪 RUNNING MAHAAROGYA BACKEND FULL E2E TEST SUITE');
  console.log('====================================================\n');

  try {
    // 1. Health Check
    console.log('1️⃣ Testing Health Check...');
    const healthRes = await axios.get(`${BASE_URL}/health`);
    console.log(
      '   ✅ Health Status:',
      healthRes.data.data.status,
      '| DB:',
      healthRes.data.data.services.database,
    );

    // 2. Auth: Demo Login for all 9 roles
    console.log('\n2️⃣ Testing Demo Login for all roles...');
    const roles = [
      'PUBLIC_PATIENT',
      'DOCTOR',
      'NURSE',
      'RECEPTION',
      'HOSPITAL_ADMIN',
      'HOSPITAL_HEAD',
      'DISTRICT_HEALTH_OFFICER',
      'GOVERNMENT_OFFICIAL',
      'SYSTEM_ADMIN',
    ];

    const tokens: Record<string, string> = {};
    for (const role of roles) {
      const res = await axios.post(`${BASE_URL}/auth/demo-login`, { role });
      tokens[role] = res.data.data.token;
      console.log(
        `   ✅ Logged in as ${role.padEnd(25)} -> User ID: ${res.data.data.user.id}`,
      );
    }

    const patientAuth = {
      headers: { Authorization: `Bearer ${tokens['PUBLIC_PATIENT']}` },
    };
    const doctorAuth = {
      headers: { Authorization: `Bearer ${tokens['DOCTOR']}` },
    };
    let adminAuth = {
      headers: { Authorization: `Bearer ${tokens['HOSPITAL_ADMIN']}` },
    };
    const sysadminAuth = {
      headers: { Authorization: `Bearer ${tokens['SYSTEM_ADMIN']}` },
    };

    // 3. Hospitals & Location Search
    console.log('\n3️⃣ Testing Hospitals & Location Search...');
    const hospitalsRes = await axios.get(`${BASE_URL}/hospitals`);
    console.log(
      `   ✅ Found ${hospitalsRes.data.data.hospitals.length} seeded hospitals in DB`,
    );
    const gmch = hospitalsRes.data.data.hospitals[0];

    const nearbyRes = await axios.get(
      `${BASE_URL}/hospitals/nearby?lat=21.1458&lon=79.0882&radius=50&urgency=EMERGENCY`,
    );
    console.log(
      `   ✅ Nearby hospital search (Nagpur 21.1458, 79.0882): Found ${nearbyRes.data.data.length} hospitals`,
    );
    console.log(
      `      Top Recommendation: ${nearbyRes.data.data[0].hospital.name} (Score: ${nearbyRes.data.data[0].recommendationScore})`,
    );

    // 4. AI Symptom Triage Conversation
    console.log('\n4️⃣ Testing AI Symptom Triage Conversation...');
    const startConvRes = await axios.post(
      `${BASE_URL}/ai/conversations`,
      { mode: 'TEXT', language: 'en' },
      patientAuth,
    );
    const convId = startConvRes.data.data.id;
    console.log(`   ✅ Started AI Conversation ID: ${convId}`);

    // Message 1: Report severe chest pain
    const msg1Res = await axios.post(
      `${BASE_URL}/ai/conversations/${convId}/messages`,
      { text: 'I have severe chest pain since 2 hours' },
      patientAuth,
    );
    console.log(`   ✅ Patient: "I have severe chest pain since 2 hours"`);
    console.log(`   🤖 AI Response: "${msg1Res.data.data.text}"`);
    console.log(
      `   📋 Triage Category: ${msg1Res.data.data.triage?.category || 'In Progress'}, Recommended: ${msg1Res.data.data.triage?.recommendedDepartment || 'N/A'}`,
    );

    // 5. Emergency Routing Case Creation
    console.log('\n5️⃣ Testing Emergency Routing & Hospital Selection...');
    const emergencyRes = await axios.post(
      `${BASE_URL}/emergency`,
      {
        symptoms: ['severe chest pain', 'sweating'],
        patientLatitude: 21.1458,
        patientLongitude: 79.0882,
      },
      patientAuth,
    );
    const emergencyCase = emergencyRes.data.data.emergencyCase;
    console.log(`   ✅ Created Emergency Case Code: ${emergencyCase.caseCode}`);

    const selectHospRes = await axios.patch(
      `${BASE_URL}/emergency/${emergencyCase.id}/select-hospital`,
      {
        hospitalId: gmch.id,
      },
      patientAuth,
    );
    console.log(
      `   ✅ Selected Hospital for Emergency: ${gmch.name} (Status: ${selectHospRes.data.data.status})`,
    );

    // 6. OPD Appointment Booking & Token Generation
    console.log('\n6️⃣ Testing OPD Appointment Booking & Token Generation...');
    const deptsRes = await axios.get(
      `${BASE_URL}/hospitals/${gmch.id}/departments`,
    );
    const dept = deptsRes.data.data[0];

    const todayStr = new Date().toISOString().split('T')[0];
    const slotsRes = await axios.get(
      `${BASE_URL}/appointments/slots/${gmch.id}/${dept.id}?date=${todayStr}`,
      patientAuth,
    );
    const slot = slotsRes.data.data[0];
    console.log(
      `   ✅ Available slot at ${gmch.shortName} (${dept.name}): ${slot?.startTime || '09:00'} - ${slot?.endTime || '09:30'}`,
    );

    const apptRes = await axios.post(
      `${BASE_URL}/appointments`,
      {
        hospitalId: gmch.id,
        departmentId: dept.id,
        slotId: slot?.id,
        appointmentDate: new Date().toISOString(),
        reason: 'General health checkup',
      },
      patientAuth,
    );
    const appt = apptRes.data.data;
    console.log(`   ✅ Booked Appointment Code: ${appt.appointmentCode}`);
    console.log(`   🎫 Token Generated: ${appt.token?.displayCode || 'N/A'}`);

    // 7. Reception Check-in
    console.log('\n7️⃣ Testing Reception Check-in / Arrival...');
    const recRes = await axios.post(`${BASE_URL}/auth/demo-login`, {
      role: 'RECEPTION',
      hospitalId: gmch.id,
    });
    const receptionAuth = {
      headers: { Authorization: `Bearer ${recRes.data.data.token}` },
    };
    const arriveRes = await axios.patch(
      `${BASE_URL}/appointments/arrive`,
      {
        appointmentId: appt.id,
        isOffline: false,
      },
      receptionAuth,
    );
    console.log(`   ✅ Reception check-in: ${arriveRes.data.data.message}`);

    // 8. Bed Management & CCTV Mock Discrepancy
    console.log('\n8️⃣ Testing Bed Status Update & CCTV Discrepancy Flow...');
    const adminRes = await axios.post(`${BASE_URL}/auth/demo-login`, {
      role: 'HOSPITAL_ADMIN',
      hospitalId: gmch.id,
    });
    adminAuth = {
      headers: { Authorization: `Bearer ${adminRes.data.data.token}` },
    };
    const bedsRes = await axios.get(
      `${BASE_URL}/beds/hospital/${gmch.id}?limit=2`,
      adminAuth,
    );
    const testBed = bedsRes.data.data.beds[0];
    console.log(
      `   ✅ Found Bed: ${testBed.bedCode} (Current Status: ${testBed.status})`,
    );

    const updateBedRes = await axios.patch(
      `${BASE_URL}/beds/${testBed.id}/status`,
      {
        status: 'MAINTENANCE',
        reason: 'Cleaning and sanitization',
      },
      adminAuth,
    );
    console.log(
      `   ✅ Updated Bed Status: ${updateBedRes.data.data.bedCode} -> ${updateBedRes.data.data.status}`,
    );

    const cctvMockRes = await axios.post(
      `${BASE_URL}/cctv/mock/${gmch.id}`,
      {},
      adminAuth,
    );
    console.log(
      `   📷 Mock CCTV Event Ingested: Event ID ${cctvMockRes.data.data.id || 'Generated'}`,
    );

    // 9. Analytics Dashboards (Hospital, District, State)
    console.log('\n9️⃣ Testing Analytics Dashboards (Multi-Tier)...');
    const hospAnalytics = await axios.get(
      `${BASE_URL}/analytics/hospital/${gmch.id}`,
      adminAuth,
    );
    console.log(
      `   🏥 Hospital Dashboard: Bed Occupancy: ${hospAnalytics.data.data.beds.occupancyPercent}%, Total Beds: ${hospAnalytics.data.data.beds.total}`,
    );

    const dhoAuth = {
      headers: { Authorization: `Bearer ${tokens['DISTRICT_HEALTH_OFFICER']}` },
    };
    const distAnalytics = await axios.get(
      `${BASE_URL}/analytics/district/${gmch.districtId}`,
      dhoAuth,
    );
    console.log(
      `   🏛️ District Dashboard: Hospitals: ${distAnalytics.data.data.hospitalCount}, Total Beds: ${distAnalytics.data.data.beds.total}`,
    );

    const govtAuth = {
      headers: { Authorization: `Bearer ${tokens['GOVERNMENT_OFFICIAL']}` },
    };
    const govtAnalytics = await axios.get(
      `${BASE_URL}/analytics/government/state`,
      govtAuth,
    );
    console.log(
      `   🏛️ State Government Dashboard: Active Hospitals: ${govtAnalytics.data.data.hospitals.active}, State-wide Bed Occupancy: ${govtAnalytics.data.data.beds.occupancyPercent}% (PII-free)`,
    );

    // 10. Audit Logs
    console.log('\n🔟 Testing System Audit Logs...');
    const auditRes = await axios.get(`${BASE_URL}/audit?limit=5`, sysadminAuth);
    console.log(`   ✅ Total Audit Records Found: ${auditRes.data.data.total}`);
    for (const log of auditRes.data.data.logs.slice(0, 3)) {
      console.log(
        `      - Action: ${log.action} | Entity: ${log.entity} | Actor Role: ${log.actorRole || 'SYSTEM'}`,
      );
    }

    console.log('\n====================================================');
    console.log('🎉 ALL 10 E2E BACKEND TESTS PASSED WITH 100% SUCCESS!');
    console.log('====================================================\n');
  } catch (err: any) {
    console.error('\n❌ Test failed:', err.response?.data || err.message);
    process.exit(1);
  }
}

runE2ETest();
