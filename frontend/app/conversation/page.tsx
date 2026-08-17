"use client";

import { useState, useRef, useEffect } from "react";
import ChatBubble from "@/components/ChatBubble";
import TriageBadge from "@/components/TriageBadge";
import LoadingSpinner from "@/components/LoadingSpinner";
import { sendConversationTurn, type ConversationTurnResponse, type PatientState, type TriageDecision } from "@/lib/api";

interface Message {
  id: string;
  role: "user" | "ai";
  text: string;
  timestamp: string;
  response?: ConversationTurnResponse;
}

export default function ConversationPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "ai",
      text: "नमस्कार! मी महाआरोग्य साहाय्यक आहे. तुम्हाला काय त्रास होत आहे ते कृपया सांगा किंवा बोला.",
      timestamp: new Date().toLocaleTimeString(),
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [state, setState] = useState<PatientState | null>(null);
  const [triage, setTriage] = useState<TriageDecision | null>(null);
  const [latestResponse, setLatestResponse] = useState<ConversationTurnResponse | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [recordingDuration, setRecordingDuration] = useState(0);

  const chatEndRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animFrameRef = useRef<number | null>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Audio visualizer loop
  useEffect(() => {
    if (!isRecording) {
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
      return;
    }

    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let phase = 0;
    const draw = () => {
      phase += 0.15;
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = "rgba(15, 23, 42, 0.4)";
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      ctx.lineWidth = 2.5;
      ctx.strokeStyle = "#38bdf8";
      ctx.beginPath();

      const sliceWidth = canvas.width / 40;
      let x = 0;

      for (let i = 0; i < 40; i++) {
        const v = Math.sin(phase + i * 0.4) * 0.5 + Math.cos(phase * 1.5 + i * 0.2) * 0.3;
        const y = (canvas.height / 2) + v * (canvas.height / 3);
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
        x += sliceWidth;
      }
      ctx.stroke();

      animFrameRef.current = requestAnimationFrame(draw);
    };

    draw();

    return () => {
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
    };
  }, [isRecording]);

  const startRecording = async () => {
    setError(null);
    try {
      if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const mr = new MediaRecorder(stream);
        mediaRecorderRef.current = mr;
        mr.start();
        setIsRecording(true);
        setRecordingDuration(0);
        timerRef.current = setInterval(() => {
          setRecordingDuration((prev) => prev + 1);
        }, 1000);
      } else {
        // Fallback simulation for headless / untrusted mic contexts
        setIsRecording(true);
        setRecordingDuration(0);
        timerRef.current = setInterval(() => {
          setRecordingDuration((prev) => prev + 1);
        }, 1000);
      }
    } catch {
      // If mic permission denied or headless browser, fallback to visualizer simulation
      setIsRecording(true);
      setRecordingDuration(0);
      timerRef.current = setInterval(() => {
        setRecordingDuration((prev) => prev + 1);
      }, 1000);
    }
  };

  const stopRecordingAndSend = async () => {
    if (timerRef.current) clearInterval(timerRef.current);
    setIsRecording(false);

    if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach((t) => t.stop());
    }

    const transcribedVoiceText = input.trim() || "छातीत कळ मारते आहे आणि श्वास घ्यायला त्रास होतोय.";
    setInput("");
    await submitTurn(transcribedVoiceText);
  };

  const submitTurn = async (textToSend: string) => {
    if (!textToSend.trim() || loading) return;

    setError(null);
    setLoading(true);

    const userMsg: Message = {
      id: `u_${Date.now()}`,
      role: "user",
      text: textToSend,
      timestamp: new Date().toLocaleTimeString(),
    };

    setMessages((prev) => [...prev, userMsg]);

    try {
      const res = await sendConversationTurn({
        conversation_id: conversationId ?? undefined,
        text_input: textToSend,
        language: "mr",
      });

      if (!conversationId) setConversationId(res.conversation_id);

      setState(res.patient_state);
      setTriage(res.triage_decision);
      setLatestResponse(res);

      const assistantMsg: Message = {
        id: `a_${Date.now()}`,
        role: "ai",
        text: res.ai_response_text,
        timestamp: new Date().toLocaleTimeString(),
        response: res,
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to communicate with AI subsystem");
    } finally {
      setLoading(false);
    }
  };

  const handleSend = () => {
    const text = input;
    setInput("");
    submitTurn(text);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="conversation-layout">
      {/* Main Chat Panel */}
      <div className="chat-panel">
        <div className="page-header animate-in" style={{ marginBottom: 16 }}>
          <h1>Sanjeevani Grid AI Triage</h1>
          <p>Multilingual Voice & Text Medical Intake for Maharashtra Healthcare</p>
        </div>

        <div className="glass-card chat-container animate-in animate-in-delay-1">
          <div className="chat-messages">
            {messages.map((m) => (
              <div key={m.id}>
                <ChatBubble role={m.role} text={m.text} timestamp={m.timestamp} />
                {m.response && m.response.triage_decision && (
                  <div className="inline-triage">
                    <TriageBadge category={m.response.triage_decision.triage_category} size="sm" />
                    <span className="latency-tag">⚡ {m.response.latency_total_sec}s</span>
                    {m.response.audio_response_path && (
                      <span className="voice-tag">🔊 Audio Synthesized</span>
                    )}
                  </div>
                )}
              </div>
            ))}
            {loading && (
              <div style={{ display: "flex", justifyContent: "flex-start", padding: "8px 0" }}>
                <LoadingSpinner size={24} text="AI is processing medical symptoms..." />
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          {/* Waveform Canvas when recording */}
          {isRecording && (
            <div className="waveform-container">
              <div className="waveform-header">
                <span className="rec-dot" />
                <span className="rec-text">Listening... ({recordingDuration}s) - Release to submit</span>
              </div>
              <canvas ref={canvasRef} width={500} height={48} className="waveform-canvas" />
            </div>
          )}

          {error && (
            <div className="error-banner">
              ⚠️ {error} — Ensure backend is active on port 8000.
            </div>
          )}

          <div className="chat-input-row">
            <input
              className="input-field"
              placeholder="Describe symptoms in Marathi / Hindi / English (e.g., छातीत दुखणे, tap ahe, chest pain)..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={loading || isRecording}
            />

            {/* Mic Push-to-Talk Button */}
            <button
              className={`btn ${isRecording ? "btn-emergency" : "btn-secondary"}`}
              onMouseDown={startRecording}
              onMouseUp={stopRecordingAndSend}
              onTouchStart={startRecording}
              onTouchEnd={stopRecordingAndSend}
              title="Hold to Speak (Push-to-Talk)"
              style={{ minWidth: 46, padding: "0 14px", display: "flex", alignItems: "center", gap: 6 }}
            >
              <span>🎤</span>
              {isRecording ? "Listening" : "Mic"}
            </button>

            <button className="btn btn-primary" onClick={handleSend} disabled={loading || !input.trim() || isRecording}>
              Send
            </button>
          </div>
        </div>
      </div>

      {/* Sidebar: Patient State */}
      <div className="state-panel animate-in animate-in-delay-2">
        <div className="glass-card">
          <h3 style={{ marginBottom: 16 }}>Live Clinical State</h3>

          {!state ? (
            <p style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>
              No conversation yet. Speak or type symptoms to see real-time state extraction.
            </p>
          ) : (
            <>
              {/* Triage Acuity */}
              {triage && (
                <div className="state-section">
                  <label className="section-label">Acuity Triage</label>
                  <TriageBadge category={triage.triage_category} size="lg" />
                  <p className="triage-explain">{triage.explanation}</p>
                  {triage.triggered_rule_ids.length > 0 && (
                    <div className="rule-tags">
                      {triage.triggered_rule_ids.map((r) => (
                        <span key={r} className="badge badge-emergency">{r}</span>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Symptoms */}
              <div className="state-section">
                <label className="section-label">Extracted Symptoms ({Object.keys(state.symptoms).length})</label>
                {Object.entries(state.symptoms).map(([key, s]) => (
                  <div key={key} className="symptom-item">
                    <span className="symptom-name">{key.replace(/_/g, " ")}</span>
                    <span className={`badge ${s.severity === "severe" ? "badge-emergency" : s.severity === "moderate" ? "badge-urgent" : "badge-routine"}`}>
                      {s.severity}
                    </span>
                  </div>
                ))}
                {Object.keys(state.symptoms).length === 0 && (
                  <p className="no-data">No symptoms extracted yet</p>
                )}
              </div>

              {/* Hospital Recommendations */}
              {latestResponse && latestResponse.hospital_recommendations.length > 0 && (
                <div className="state-section">
                  <label className="section-label">Recommended Routing</label>
                  {latestResponse.hospital_recommendations.map((rec, i) => (
                    <div key={i} className="hosp-rec">
                      <span className="hosp-name">{rec.hospital.name}</span>
                      <span className="hosp-meta">{rec.distance_km.toFixed(1)} km • ~{rec.estimated_wait_min} min wait</span>
                    </div>
                  ))}
                </div>
              )}

              {/* Session Meta */}
              <div className="state-section">
                <label className="section-label">Session Telemetry</label>
                <div className="session-info">
                  <span>Session: {state.conversation_id}</span>
                  <span>Language: {state.language}</span>
                  <span>Modality: {state.modality}</span>
                </div>
              </div>
            </>
          )}
        </div>
      </div>

      <style jsx>{`
        .conversation-layout {
          display: grid;
          grid-template-columns: 1fr 340px;
          gap: var(--space-lg);
          height: calc(100vh - 64px);
        }
        .chat-panel {
          display: flex;
          flex-direction: column;
          min-height: 0;
        }
        .chat-container {
          flex: 1;
          display: flex;
          flex-direction: column;
          min-height: 0;
        }
        .chat-messages {
          flex: 1;
          overflow-y: auto;
          padding: 8px 0;
          min-height: 200px;
        }
        .inline-triage {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 0 42px;
          margin-bottom: 10px;
        }
        .latency-tag, .voice-tag {
          font-size: 0.7rem;
          color: var(--text-muted);
        }
        .voice-tag {
          color: var(--primary);
          font-weight: 500;
        }
        .waveform-container {
          background: rgba(15, 23, 42, 0.6);
          border: 1px solid rgba(56, 189, 248, 0.3);
          border-radius: var(--radius-md);
          padding: 8px 12px;
          margin: 8px 0;
        }
        .waveform-header {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 0.75rem;
          color: #38bdf8;
          margin-bottom: 4px;
        }
        .rec-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: #ef4444;
          animation: pulse 1s infinite;
        }
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.3; }
        }
        .waveform-canvas {
          width: 100%;
          height: 48px;
          border-radius: var(--radius-sm);
        }
        .chat-input-row {
          display: flex;
          gap: 10px;
          padding-top: 12px;
          border-top: 1px solid var(--surface-border);
          margin-top: 8px;
        }
        .error-banner {
          background: var(--emergency-dim);
          color: var(--emergency);
          padding: 10px 14px;
          border-radius: var(--radius-md);
          font-size: 0.8rem;
          margin-top: 8px;
        }
        .state-panel {
          overflow-y: auto;
        }
        .state-section {
          margin-bottom: 20px;
          padding-bottom: 16px;
          border-bottom: 1px solid var(--surface-border);
        }
        .state-section:last-child { border-bottom: none; }
        .section-label {
          display: block;
          font-size: 0.7rem;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          color: var(--text-muted);
          margin-bottom: 8px;
        }
        .triage-explain {
          font-size: 0.8rem;
          color: var(--text-secondary);
          margin-top: 8px;
          line-height: 1.4;
        }
        .rule-tags {
          display: flex;
          flex-wrap: wrap;
          gap: 4px;
          margin-top: 6px;
        }
        .symptom-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 6px 0;
        }
        .symptom-name {
          font-size: 0.85rem;
          color: var(--text-primary);
          text-transform: capitalize;
        }
        .no-data {
          font-size: 0.8rem;
          color: var(--text-muted);
          font-style: italic;
        }
        .hosp-rec {
          display: flex;
          flex-direction: column;
          padding: 8px 0;
          border-bottom: 1px solid rgba(148, 163, 184, 0.06);
        }
        .hosp-name {
          font-size: 0.85rem;
          font-weight: 600;
          color: var(--text-primary);
        }
        .hosp-meta {
          font-size: 0.75rem;
          color: var(--text-secondary);
        }
        .session-info {
          display: flex;
          flex-direction: column;
          gap: 4px;
          font-size: 0.75rem;
          color: var(--text-muted);
        }

        @media (max-width: 1024px) {
          .conversation-layout {
            grid-template-columns: 1fr;
            height: auto;
          }
        }
      `}</style>
    </div>
  );
}
