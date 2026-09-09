import { Injectable, Logger } from '@nestjs/common';
import {
  AIServiceInterface,
  TranscribeResult,
  ExtractedMedicalInfo,
  TriageResult,
  AIResponse,
  PatientStateUpdate,
} from './ai.interface';

// ============================================================
// MOCK AI SERVICE
// This simulates an AI without any real ML model.
// Replace this with a real AI adapter (local Ollama, local model, etc.)
// when the ML team is ready.
// ============================================================

interface SymptomRule {
  keywords: string[];
  symptom: string;
  bodyLocation?: string;
  triageCategory?: 'ROUTINE' | 'PRIORITY' | 'URGENT' | 'EMERGENCY';
  department?: string;
}

const SYMPTOM_RULES: SymptomRule[] = [
  {
    keywords: ['chest pain', 'chest dard', 'chhati dukhtay', 'chest dukhtay'],
    symptom: 'chest pain',
    bodyLocation: 'chest',
    triageCategory: 'EMERGENCY',
    department: 'Cardiology',
  },
  {
    keywords: ['breathing', 'breath', 'श्वास', 'dama', 'asthma'],
    symptom: 'breathing difficulty',
    bodyLocation: 'chest',
    triageCategory: 'URGENT',
    department: 'Pulmonology',
  },
  {
    keywords: ['pot dukhtay', 'pet dard', 'stomach', 'abdominal', 'belly'],
    symptom: 'abdominal pain',
    bodyLocation: 'abdomen',
    triageCategory: 'ROUTINE',
    department: 'General Medicine',
  },
  {
    keywords: ['head', 'sir dukhtay', 'headache', 'डोकेदुखी'],
    symptom: 'headache',
    bodyLocation: 'head',
    triageCategory: 'ROUTINE',
    department: 'General Medicine',
  },
  {
    keywords: ['fever', 'taap', 'ताप', 'bukhar', 'temperature'],
    symptom: 'fever',
    triageCategory: 'ROUTINE',
    department: 'General Medicine',
  },
  {
    keywords: ['vomiting', 'ulti', 'उलटी', 'nausea'],
    symptom: 'vomiting/nausea',
    triageCategory: 'ROUTINE',
    department: 'General Medicine',
  },
  {
    keywords: [
      'stroke',
      'paralysis',
      'face droop',
      'arm weakness',
      'speech slurred',
    ],
    symptom: 'stroke symptoms',
    triageCategory: 'EMERGENCY',
    department: 'Neurology',
  },
  {
    keywords: ['accident', 'injury', 'fracture', 'broken', 'trauma'],
    symptom: 'trauma/injury',
    triageCategory: 'URGENT',
    department: 'Emergency',
  },
  {
    keywords: ['pregnancy', 'labour', 'delivery', 'pregnant'],
    symptom: 'obstetric concern',
    triageCategory: 'URGENT',
    department: 'Obstetrics',
  },
  {
    keywords: ['child', 'baby', 'infant', 'bal', 'मुल'],
    symptom: 'pediatric concern',
    triageCategory: 'PRIORITY',
    department: 'Pediatrics',
  },
];

const FOLLOW_UP_QUESTIONS: Record<string, Record<string, string[]>> = {
  en: {
    duration: [
      'How long have you had this symptom?',
      'When did this start?',
      'How many days has this been going on?',
    ],
    severity: [
      'On a scale of 1-10, how severe is the pain?',
      'Is the pain mild, moderate, or severe?',
      'Does it stop you from doing daily activities?',
    ],
    vomiting: ['Are you experiencing any vomiting or nausea?'],
    fever: ['Do you have a fever?'],
    progression: ['Is it getting better or worse over time?'],
    associated: ['Do you have any other symptoms?'],
  },
  mr: {
    duration: ['Kadhi pasun aahe he?', 'Kitya divs pasun aahe?'],
    severity: ['1 te 10 madhye kiti tras aahe?', 'Dard halka aahe ki kharach?'],
    vomiting: ['Ulti hote ka?'],
    fever: ['Taap aahe ka?'],
    associated: ['Itar kaahi tras aahe ka?'],
  },
  hi: {
    duration: ['Kab se hai?', 'Kitne dino se hai?'],
    severity: ['1 se 10 mein kitna dard hai?'],
    vomiting: ['Ulti ho rahi hai?'],
    fever: ['Bukhar hai?'],
    associated: ['Aur koi takleef hai?'],
  },
};

@Injectable()
export class MockAIService implements AIServiceInterface {
  private readonly logger = new Logger(MockAIService.name);

  constructor() {
    this.logger.warn(
      '⚠️  MOCK AI SERVICE ACTIVE — No real AI model connected. Replace with real AIService when ready.',
    );
  }

  isAvailable(): boolean {
    return true; // Mock is always available
  }

  async transcribe(
    audioBuffer: Buffer,
    language = 'auto',
  ): Promise<TranscribeResult> {
    // Mock: pretend to transcribe
    return {
      text: '[MOCK TRANSCRIPTION — Connect real ASR model]',
      language: language === 'auto' ? 'en' : language,
      confidence: 0.75,
    };
  }

  async detectLanguage(text: string): Promise<string> {
    // Simple heuristic detection
    const marathiIndicators = [
      'aahe',
      'dukhtay',
      'aahot',
      'nahi',
      'kadhi',
      'pasun',
      'mazha',
      'majha',
    ];
    const hindiIndicators = [
      'hai',
      'ho',
      'raha',
      'karo',
      'mujhe',
      'mera',
      'tera',
    ];

    const lower = text.toLowerCase();
    if (marathiIndicators.some((w) => lower.includes(w))) return 'mr';
    if (hindiIndicators.some((w) => lower.includes(w))) return 'hi';
    // Check for Devanagari script
    if (/[\u0900-\u097F]/.test(text)) return 'hi';
    return 'en';
  }

  async extractMedicalInfo(
    text: string,
    language: string,
    conversationHistory: Array<{ role: string; content: string }>,
  ): Promise<ExtractedMedicalInfo> {
    const lower = text.toLowerCase();
    const extracted: ExtractedMedicalInfo = {
      symptoms: [],
      bodyLocations: [],
      language,
      onset: undefined,
      duration: undefined,
      severity: undefined,
    };

    // Match symptom rules
    for (const rule of SYMPTOM_RULES) {
      if (rule.keywords.some((k) => lower.includes(k))) {
        if (!extracted.symptoms.includes(rule.symptom)) {
          extracted.symptoms.push(rule.symptom);
        }
        if (
          rule.bodyLocation &&
          !extracted.bodyLocations.includes(rule.bodyLocation)
        ) {
          extracted.bodyLocations.push(rule.bodyLocation);
        }
      }
    }

    // Extract duration patterns
    const durationPatterns = [
      /(\d+)\s*(din|day|divas|ghanta|hour|minute)/i,
      /(ek|do|teen|char|panch|ek|one|two|three|four|five)\s*(din|day|divas)/i,
    ];
    for (const pattern of durationPatterns) {
      const match = text.match(pattern);
      if (match) {
        extracted.duration = match[0];
        break;
      }
    }

    // Severity extraction
    if (/kharach|bahut|very|severe|extreme|10/i.test(text))
      extracted.severity = 'severe';
    else if (/thoda|halka|mild|little/i.test(text)) extracted.severity = 'mild';
    else if (/moderate|medium/i.test(text)) extracted.severity = 'moderate';

    // Safety signals
    const safetyPatterns = [
      { pattern: /chest pain|chhati/i, signal: 'CHEST_PAIN' },
      { pattern: /breathing|breath/i, signal: 'BREATHING_DIFFICULTY' },
      { pattern: /unconscious|faint/i, signal: 'LOSS_OF_CONSCIOUSNESS' },
      { pattern: /bleeding|blood/i, signal: 'BLEEDING' },
      { pattern: /stroke|paralysis/i, signal: 'STROKE_SYMPTOMS' },
    ];
    extracted.safetySignals = [];
    for (const sp of safetyPatterns) {
      if (sp.pattern.test(text)) extracted.safetySignals.push(sp.signal);
    }

    return extracted;
  }

  async getNextQuestion(
    patientState: Record<string, unknown>,
    language: string,
  ): Promise<string> {
    const lang = ['en', 'mr', 'hi'].includes(language) ? language : 'en';
    const qs = FOLLOW_UP_QUESTIONS[lang];

    // Determine what we still need to know
    if (!patientState.duration) {
      const questions = qs.duration;
      return questions[Math.floor(Math.random() * questions.length)];
    }
    if (!patientState.severity) {
      const questions = qs.severity;
      return questions[Math.floor(Math.random() * questions.length)];
    }
    if (!patientState.vomiting) {
      return qs.vomiting[0];
    }
    if (!patientState.fever) {
      return qs.fever[0];
    }
    if (!patientState.associated) {
      return qs.associated[0];
    }

    return lang === 'mr'
      ? 'Dhanyawaad. Aamhi tumhala sahay kartoy.'
      : lang === 'hi'
        ? 'Dhanyawad. Hum aapki madad kar rahe hain.'
        : 'Thank you. We are finding the best care option for you.';
  }

  async triage(patientState: Record<string, unknown>): Promise<TriageResult> {
    const symptoms = (patientState.symptoms as string[]) || [];
    const safetySignals = (patientState.safetySignals as string[]) || [];

    let category: TriageResult['category'] = 'ROUTINE';
    let department = 'General Medicine';
    let confidence = 0.65;

    // Safety signals always elevate
    if (
      safetySignals.includes('CHEST_PAIN') ||
      safetySignals.includes('STROKE_SYMPTOMS') ||
      safetySignals.includes('LOSS_OF_CONSCIOUSNESS')
    ) {
      category = 'EMERGENCY';
      confidence = 0.91;
    } else if (
      safetySignals.includes('BREATHING_DIFFICULTY') ||
      safetySignals.includes('BLEEDING')
    ) {
      category = 'URGENT';
      confidence = 0.85;
    }

    // Match rules for department and category
    for (const rule of SYMPTOM_RULES) {
      if (symptoms.includes(rule.symptom)) {
        if (rule.department) department = rule.department;
        if (rule.triageCategory) {
          const categories = ['ROUTINE', 'PRIORITY', 'URGENT', 'EMERGENCY'];
          if (
            categories.indexOf(rule.triageCategory) >
            categories.indexOf(category)
          ) {
            category = rule.triageCategory;
          }
        }
      }
    }

    const reasoningMap: Record<string, string> = {
      ROUTINE: 'Symptoms suggest a non-urgent condition suitable for OPD.',
      PRIORITY: 'Symptoms suggest a condition requiring timely attention.',
      URGENT:
        'Symptoms suggest an urgent condition requiring prompt evaluation.',
      EMERGENCY: 'Symptoms suggest a potentially life-threatening emergency.',
    };

    return {
      category,
      confidence,
      recommendedDepartment: department,
      reasoning: reasoningMap[category],
      safetySignals,
      modelVersion: 'MOCK_AI_v1.0',
      isMock: true,
    };
  }

  async generateResponse(
    text: string,
    patientState: Record<string, unknown>,
    language: string,
  ): Promise<AIResponse> {
    const extractedInfo = await this.extractMedicalInfo(text, language, []);

    // Update state
    const stateUpdate: PatientStateUpdate = {};
    if (extractedInfo.symptoms.length > 0) {
      const existingSymptoms = (patientState.symptoms as string[]) || [];
      stateUpdate.symptoms = [
        ...new Set([...existingSymptoms, ...extractedInfo.symptoms]),
      ];
    }
    if (extractedInfo.duration) stateUpdate.duration = extractedInfo.duration;
    if (extractedInfo.severity) stateUpdate.severity = extractedInfo.severity;
    if (extractedInfo.safetySignals?.length)
      stateUpdate.safetySignals = extractedInfo.safetySignals;

    const updatedState = { ...patientState, ...stateUpdate };

    // Decide if we have enough info to triage
    const hasSymptoms = ((updatedState.symptoms as string[]) || []).length > 0;
    const hasDuration = !!updatedState.duration;
    const turnNumber = (updatedState.turnNumber as number) || 0;
    const isComplete = hasSymptoms && hasDuration && turnNumber >= 2;

    let responseText: string;
    let suggestedTriage: TriageResult | undefined;

    if (isComplete || (extractedInfo.safetySignals || []).length > 0) {
      suggestedTriage = await this.triage(updatedState);
      const lang = language;
      if (suggestedTriage.category === 'EMERGENCY') {
        responseText =
          lang === 'mr'
            ? 'He symptoms gambhir disun yetaat. Turant rugnalayat jaane aavashyak aahe.'
            : lang === 'hi'
              ? 'Ye symptoms gambhir lag rahe hain. Turant hospital jaana zaroori hai.'
              : '⚠️ Your symptoms appear serious. Immediate emergency care is recommended.';
      } else {
        responseText =
          lang === 'mr'
            ? `Dhanyawaad. Tumchi triage category: ${suggestedTriage.category}. ${suggestedTriage.recommendedDepartment} department shiftarit jaane sucharavet aahe.`
            : lang === 'hi'
              ? `Dhanyawad. Aapki triage category: ${suggestedTriage.category}. ${suggestedTriage.recommendedDepartment} department mein jaane ki salah hai.`
              : `Thank you. Based on your symptoms, we recommend visiting ${suggestedTriage.recommendedDepartment}. Category: ${suggestedTriage.category}.`;
      }
    } else {
      const nextQ = await this.getNextQuestion(updatedState, language);
      responseText = nextQ;
    }

    return {
      text: responseText,
      isComplete,
      suggestedTriage,
      extractedInfo,
      stateUpdate,
    };
  }

  async synthesizeSpeech(text: string, language: string): Promise<Buffer> {
    // Mock: return empty buffer — connect real TTS here
    this.logger.warn(
      'synthesizeSpeech called on MockAIService — returning empty buffer',
    );
    return Buffer.from(`[MOCK TTS: ${text.substring(0, 50)}]`);
  }
}
