/**
 * TypeScript type definitions for HCPilot AI frontend.
 */

// ─── Interaction Form Data ───────────────────────────────────
export interface InteractionFormData {
  id?: number;
  hcp_id?: number;
  hcp_name: string;
  interaction_type: string;
  meeting_date: string;
  meeting_time: string;
  attendees: string;
  topics_discussed: string;
  products_discussed: string;
  materials_shared: string;
  samples_distributed: string;
  sentiment: string;
  summary: string;
  follow_up_date: string;
  notes: string;
  created_at?: string;
  updated_at?: string;
}

// ─── Chat ────────────────────────────────────────────────────
export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  toolUsed?: string | null;
  timestamp: string;
  updatedFields?: string[];
}

export interface ChatRequest {
  message: string;
  conversation_history: Array<{ role: string; content: string }>;
  current_form_data?: Partial<InteractionFormData> | null;
  interaction_id?: number | null;
}

export interface ChatResponse {
  ai_message: string;
  tool_used: string | null;
  form_data: InteractionFormData | null;
  interaction_id: number | null;
  search_results: Array<Record<string, unknown>> | null;
  updated_fields: string[];
}

// ─── HCP ─────────────────────────────────────────────────────
export interface HCP {
  id: number;
  name: string;
  specialization: string;
  hospital: string;
  city: string;
}

// ─── Redux State Shapes ──────────────────────────────────────
export interface InteractionState {
  formData: InteractionFormData;
  interactionId: number | null;
  highlightedFields: string[];
  isNew: boolean;
}

export interface ChatState {
  messages: ChatMessage[];
  isLoading: boolean;
  currentTool: string | null;
  error: string | null;
}

// ─── Utility ─────────────────────────────────────────────────
export const EMPTY_FORM: InteractionFormData = {
  hcp_name: "",
  interaction_type: "",
  meeting_date: "",
  meeting_time: "",
  attendees: "",
  topics_discussed: "",
  products_discussed: "",
  materials_shared: "",
  samples_distributed: "",
  sentiment: "",
  summary: "",
  follow_up_date: "",
  notes: "",
};

export const INTERACTION_TYPES = [
  "Meeting",
  "In-Person",
  "Virtual",
  "Phone Call",
  "Email",
  "Conference",
];

export const SENTIMENTS = ["Positive", "Neutral", "Negative"];

export const TOOL_LABELS: Record<string, string> = {
  log_interaction: "📝 Log Interaction",
  edit_interaction: "✏️ Edit Interaction",
  search_interaction: "🔍 Search Interaction",
  generate_followup: "📋 Generate Follow-up",
  interaction_summary: "📊 Interaction Summary",
  general: "💬 General",
};
