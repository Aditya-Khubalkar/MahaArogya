"use client";

interface ChatBubbleProps {
  role: "user" | "ai";
  text: string;
  timestamp?: string;
}

export default function ChatBubble({ role, text, timestamp }: ChatBubbleProps) {
  const isAI = role === "ai";

  return (
    <div className={`bubble-row ${isAI ? "ai-row" : "user-row"}`}>
      {isAI && <div className="avatar ai-avatar">🤖</div>}
      <div className={`bubble ${isAI ? "ai-bubble" : "user-bubble"}`}>
        <p className="bubble-text">{text}</p>
        {timestamp && <span className="bubble-time">{timestamp}</span>}
      </div>
      {!isAI && <div className="avatar user-avatar">👤</div>}

      <style jsx>{`
        .bubble-row {
          display: flex;
          align-items: flex-end;
          gap: 10px;
          margin-bottom: 14px;
          animation: fadeInUp 0.3s ease both;
        }
        .user-row { justify-content: flex-end; }
        .ai-row { justify-content: flex-start; }

        .avatar {
          width: 32px;
          height: 32px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 1rem;
          flex-shrink: 0;
        }
        .ai-avatar { background: var(--primary-dim); }
        .user-avatar { background: var(--accent-dim); }

        .bubble {
          max-width: 70%;
          padding: 12px 16px;
          border-radius: 16px;
          position: relative;
        }
        .ai-bubble {
          background: var(--surface);
          border: 1px solid var(--surface-border);
          border-bottom-left-radius: 4px;
        }
        .user-bubble {
          background: var(--primary-dim);
          border: 1px solid rgba(6, 214, 160, 0.2);
          border-bottom-right-radius: 4px;
        }

        .bubble-text {
          font-size: 0.9rem;
          line-height: 1.5;
          color: var(--text-primary);
          white-space: pre-wrap;
        }

        .bubble-time {
          display: block;
          font-size: 0.65rem;
          color: var(--text-muted);
          margin-top: 6px;
          text-align: right;
        }
      `}</style>
    </div>
  );
}
