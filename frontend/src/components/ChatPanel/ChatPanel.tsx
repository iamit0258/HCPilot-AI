/**
 * ChatPanel — AI Assistant chat interface (right side).
 * ChatGPT-style conversation with tool status indicators.
 */
import { useState, useRef, useEffect } from "react";
import { useSelector, useDispatch } from "react-redux";
import type { RootState, AppDispatch } from "../../redux/store";
import { sendMessage, addUserMessage } from "../../redux/chatSlice";
import { clearForm } from "../../redux/interactionSlice";
import type { ChatMessage } from "../../types";
import { TOOL_LABELS } from "../../types";
import "./ChatPanel.css";

const QUICK_PROMPTS = [
  "Log a new interaction",
  "Edit the last interaction",
  "Search past meetings",
  "Suggest follow-up actions",
  "Summarize interactions",
];

export default function ChatPanel() {
  const dispatch = useDispatch<AppDispatch>();
  const { messages, isLoading, currentTool } = useSelector(
    (state: RootState) => state.chat
  );
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  // Auto-resize textarea
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.style.height = "auto";
      inputRef.current.style.height = `${Math.min(inputRef.current.scrollHeight, 120)}px`;
    }
  }, [input]);

  const handleSend = () => {
    const trimmed = input.trim();
    if (!trimmed || isLoading) return;

    // Add user message to chat
    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      content: trimmed,
      timestamp: new Date().toISOString(),
    };
    dispatch(addUserMessage(userMsg));

    // Send to AI agent
    dispatch(sendMessage(trimmed));
    setInput("");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleQuickPrompt = (prompt: string) => {
    setInput(prompt);
    inputRef.current?.focus();
  };

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString("en-US", {
      hour: "numeric",
      minute: "2-digit",
      hour12: true,
    });
  };

  const renderMarkdown = (text: string) => {
    // Simple markdown: bold, bullet points, newlines
    return text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/^• (.*)$/gm, '<li>$1</li>')
      .replace(/^  • (.*)$/gm, '<li class="nested">$1</li>')
      .replace(/\n/g, '<br/>');
  };

  return (
    <div className="chat-panel">
      {/* Header */}
      <div className="chat-header">
        <div className="chat-header-left">
          <div className="chat-avatar">
            <span>🤖</span>
          </div>
          <div>
            <h2 className="chat-title">AI Assistant</h2>
            <p className="chat-subtitle">Log Interaction details here via chat</p>
          </div>
        </div>
        {currentTool && currentTool !== "general" && (
          <div className="tool-badge">
            {TOOL_LABELS[currentTool] || currentTool}
          </div>
        )}
      </div>

      {/* Messages Area */}
      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="chat-welcome">
            {/* Welcome info box */}
            <div className="welcome-card">
              <p>
                Log interaction details here (e.g., "Met Dr. Smith, discussed
                Prodo-X efficacy, positive sentiment, shared brochure") or ask
                for help.
              </p>
            </div>

            {/* Quick prompts */}
            <div className="quick-prompts">
              <p className="quick-prompts-label">Try these:</p>
              <div className="quick-prompts-grid">
                {QUICK_PROMPTS.map((prompt) => (
                  <button
                    key={prompt}
                    className="quick-prompt-chip"
                    onClick={() => handleQuickPrompt(prompt)}
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`message ${msg.role === "user" ? "message-user" : "message-ai"}`}
          >
            {msg.role === "assistant" && (
              <div className="message-avatar">🤖</div>
            )}
            <div className="message-content">
              {msg.toolUsed && msg.toolUsed !== "general" && (
                <div className="message-tool-tag">
                  {TOOL_LABELS[msg.toolUsed] || msg.toolUsed}
                </div>
              )}
              <div
                className="message-text"
                dangerouslySetInnerHTML={{ __html: renderMarkdown(msg.content) }}
              />
              <span className="message-time">{formatTime(msg.timestamp)}</span>
            </div>
            {msg.role === "user" && (
              <div className="message-avatar user-avatar">👤</div>
            )}
          </div>
        ))}

        {/* Typing indicator */}
        {isLoading && (
          <div className="message message-ai">
            <div className="message-avatar">🤖</div>
            <div className="message-content">
              <div className="typing-indicator">
                <span /><span /><span />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="chat-input-area">
        <div className="chat-input-wrapper">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Describe Interaction..."
            className="chat-input"
            rows={1}
            disabled={isLoading}
          />
          <button
            className={`chat-send-btn ${input.trim() && !isLoading ? "active" : ""}`}
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            title="Send message"
          >
            {isLoading ? (
              <div className="send-spinner" />
            ) : (
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/>
              </svg>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
