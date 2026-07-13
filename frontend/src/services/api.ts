/**
 * API service layer — handles all HTTP communication with the FastAPI backend.
 */
import axios from "axios";
import type { ChatRequest, ChatResponse, InteractionFormData, HCP } from "../types";

const api = axios.create({
  baseURL: "http://localhost:8000/api",
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30000, // 30s timeout for LLM calls
});

/**
 * Send a chat message to the AI agent.
 */
export async function sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
  const response = await api.post<ChatResponse>("/chat", request);
  return response.data;
}

/**
 * Get all interactions.
 */
export async function getInteractions(): Promise<InteractionFormData[]> {
  const response = await api.get<InteractionFormData[]>("/interactions");
  return response.data;
}

/**
 * Get a single interaction by ID.
 */
export async function getInteraction(id: number): Promise<InteractionFormData> {
  const response = await api.get<InteractionFormData>(`/interactions/${id}`);
  return response.data;
}

/**
 * Get all HCPs.
 */
export async function getHCPs(): Promise<HCP[]> {
  const response = await api.get<HCP[]>("/hcps");
  return response.data;
}

/**
 * Health check.
 */
export async function healthCheck(): Promise<{ status: string }> {
  const response = await api.get<{ status: string }>("/health");
  return response.data;
}

export default api;
