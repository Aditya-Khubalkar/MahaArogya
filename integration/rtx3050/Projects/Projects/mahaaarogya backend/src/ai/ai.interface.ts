// AI Service Interface — the backend depends on this, not on any specific AI implementation

export interface TranscribeResult {
  text: string;
  language: string;
  confidence: number;
}

export interface ExtractedMedicalInfo {
  symptoms: string[];
  bodyLocations: string[];
  onset?: string;
  duration?: string;
  severity?: string;
  progression?: string;
  frequency?: string;
  associatedSymptoms?: string[];
  negations?: string[];
  safetySignals?: string[];
  language: string;
}

export interface PatientStateUpdate {
  symptoms?: string[];
  bodyLocations?: string[];
  onset?: string;
  duration?: string;
  severity?: string;
  language?: string;
  safetySignals?: string[];
  [key: string]: unknown;
}

export interface TriageResult {
  category: 'ROUTINE' | 'PRIORITY' | 'URGENT' | 'EMERGENCY';
  confidence: number;
  recommendedDepartment: string;
  reasoning: string;
  safetySignals: string[];
  modelVersion: string;
  isMock: boolean;
}

export interface AIResponse {
  text: string;
  audioBase64?: string; // For voice mode
  nextQuestion?: string;
  isComplete: boolean;
  suggestedTriage?: TriageResult;
  extractedInfo?: ExtractedMedicalInfo;
  stateUpdate?: PatientStateUpdate;
}

export interface AIServiceInterface {
  transcribe(audioBuffer: Buffer, language?: string): Promise<TranscribeResult>;
  detectLanguage(text: string): Promise<string>;
  extractMedicalInfo(
    text: string,
    language: string,
    conversationHistory: Array<{ role: string; content: string }>,
  ): Promise<ExtractedMedicalInfo>;
  getNextQuestion(
    patientState: Record<string, unknown>,
    language: string,
  ): Promise<string>;
  triage(patientState: Record<string, unknown>): Promise<TriageResult>;
  generateResponse(
    text: string,
    patientState: Record<string, unknown>,
    language: string,
  ): Promise<AIResponse>;
  synthesizeSpeech(text: string, language: string): Promise<Buffer>;
  isAvailable(): boolean;
}

export const AI_SERVICE_TOKEN = 'AI_SERVICE';
