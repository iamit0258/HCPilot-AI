/**
 * FormPanel — Read-only CRM form that displays interaction data populated by the AI.
 * Fields glow/highlight when the AI updates them.
 */
import { useEffect } from "react";
import { useSelector, useDispatch } from "react-redux";
import type { RootState, AppDispatch } from "../../redux/store";
import { clearHighlights, clearForm } from "../../redux/interactionSlice";
import { INTERACTION_TYPES, SENTIMENTS } from "../../types";
import "./FormPanel.css";

export default function FormPanel() {
  const dispatch = useDispatch<AppDispatch>();
  const { formData, highlightedFields, isNew } = useSelector(
    (state: RootState) => state.interaction
  );

  // Clear highlights after animation
  useEffect(() => {
    if (highlightedFields.length > 0) {
      const timer = setTimeout(() => dispatch(clearHighlights()), 2500);
      return () => clearTimeout(timer);
    }
  }, [highlightedFields, dispatch]);

  const isHighlighted = (field: string) => highlightedFields.includes(field);

  const handleNewInteraction = () => {
    dispatch(clearForm());
  };

  return (
    <div className="form-panel">
      {/* Header */}
      <div className="form-header">
        <div className="form-header-left">
          <div className="form-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <line x1="16" y1="13" x2="8" y2="13"/>
              <line x1="16" y1="17" x2="8" y2="17"/>
              <polyline points="10 9 9 9 8 9"/>
            </svg>
          </div>
          <div>
            <h2 className="form-title">Log HCP Interaction</h2>
            <p className="form-subtitle">Interaction Details</p>
          </div>
        </div>
        <button className="btn-new" onClick={handleNewInteraction} title="New Interaction">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
          New
        </button>
      </div>

      {/* Form Body */}
      <div className="form-body">
        {/* Row: HCP Name + Interaction Type */}
        <div className="form-row">
          <div className={`form-group ${isHighlighted("hcp_name") ? "highlighted" : ""}`}>
            <label>HCP Name</label>
            <input
              type="text"
              value={formData.hcp_name}
              readOnly
              placeholder="Search or select HCP..."
              className="form-input"
            />
          </div>
          <div className={`form-group ${isHighlighted("interaction_type") ? "highlighted" : ""}`}>
            <label>Interaction Type</label>
            <select
              value={formData.interaction_type}
              disabled
              className="form-input form-select"
            >
              <option value="">Select type...</option>
              {INTERACTION_TYPES.map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Row: Date + Time */}
        <div className="form-row">
          <div className={`form-group ${isHighlighted("meeting_date") ? "highlighted" : ""}`}>
            <label>Date</label>
            <input
              type="text"
              value={formData.meeting_date}
              readOnly
              placeholder="MM/DD/YYYY"
              className="form-input"
            />
          </div>
          <div className={`form-group ${isHighlighted("meeting_time") ? "highlighted" : ""}`}>
            <label>Time</label>
            <input
              type="text"
              value={formData.meeting_time}
              readOnly
              placeholder="HH:MM AM/PM"
              className="form-input"
            />
          </div>
        </div>

        {/* Attendees */}
        <div className={`form-group full ${isHighlighted("attendees") ? "highlighted" : ""}`}>
          <label>Attendees</label>
          <input
            type="text"
            value={formData.attendees}
            readOnly
            placeholder="Enter names or search..."
            className="form-input"
          />
        </div>

        {/* Topics Discussed */}
        <div className={`form-group full ${isHighlighted("topics_discussed") ? "highlighted" : ""}`}>
          <label>Topics Discussed</label>
          <textarea
            value={formData.topics_discussed}
            readOnly
            placeholder="Enter key discussion points..."
            className="form-input form-textarea"
            rows={2}
          />
        </div>

        {/* Products Discussed */}
        <div className={`form-group full ${isHighlighted("products_discussed") ? "highlighted" : ""}`}>
          <label>Products Discussed</label>
          <input
            type="text"
            value={formData.products_discussed}
            readOnly
            placeholder="Products discussed during interaction..."
            className="form-input"
          />
        </div>

        {/* Materials + Samples */}
        <div className="form-row">
          <div className={`form-group ${isHighlighted("materials_shared") ? "highlighted" : ""}`}>
            <label>Materials Shared</label>
            <input
              type="text"
              value={formData.materials_shared}
              readOnly
              placeholder="Brochures, presentations..."
              className="form-input"
            />
          </div>
          <div className={`form-group ${isHighlighted("samples_distributed") ? "highlighted" : ""}`}>
            <label>Samples Distributed</label>
            <input
              type="text"
              value={formData.samples_distributed}
              readOnly
              placeholder="Product samples..."
              className="form-input"
            />
          </div>
        </div>

        {/* Sentiment */}
        <div className={`form-group full ${isHighlighted("sentiment") ? "highlighted" : ""}`}>
          <label>Sentiment</label>
          <div className="sentiment-chips">
            {SENTIMENTS.map((s) => (
              <span
                key={s}
                className={`sentiment-chip ${s.toLowerCase()} ${
                  formData.sentiment?.toLowerCase() === s.toLowerCase() ? "active" : ""
                }`}
              >
                <span className="sentiment-dot" />
                {s}
              </span>
            ))}
          </div>
        </div>

        {/* Follow-up Date */}
        <div className={`form-group full ${isHighlighted("follow_up_date") ? "highlighted" : ""}`}>
          <label>Follow-up Date</label>
          <input
            type="text"
            value={formData.follow_up_date}
            readOnly
            placeholder="Follow-up date..."
            className="form-input"
          />
        </div>

        {/* Summary */}
        <div className={`form-group full ${isHighlighted("summary") ? "highlighted" : ""}`}>
          <label>Summary</label>
          <textarea
            value={formData.summary}
            readOnly
            placeholder="AI-generated summary will appear here..."
            className="form-input form-textarea"
            rows={2}
          />
        </div>

        {/* Notes */}
        <div className={`form-group full ${isHighlighted("notes") ? "highlighted" : ""}`}>
          <label>Notes</label>
          <textarea
            value={formData.notes}
            readOnly
            placeholder="Additional notes..."
            className="form-input form-textarea"
            rows={2}
          />
        </div>

        {/* AI Controlled Badge */}
        <div className="form-ai-badge">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>
          </svg>
          <span>Form is AI-controlled — use the assistant to update fields</span>
        </div>
      </div>
    </div>
  );
}
