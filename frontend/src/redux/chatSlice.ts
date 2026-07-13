/**
 * Chat Redux slice — manages AI assistant messages and loading state.
 */
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import type { PayloadAction } from "@reduxjs/toolkit";
import type { ChatState, ChatMessage, ChatResponse } from "../types";
import { sendChatMessage } from "../services/api";
import type { RootState } from "./store";
import {
  setFormData,
  setInteractionId,
  setHighlightedFields,
} from "./interactionSlice";

const initialState: ChatState = {
  messages: [],
  isLoading: false,
  currentTool: null,
  error: null,
};

/**
 * Async thunk: send a message to the AI agent and process the response.
 */
export const sendMessage = createAsyncThunk<
  ChatResponse,
  string,
  { state: RootState }
>("chat/sendMessage", async (message, { getState, dispatch }) => {
  const state = getState();
  const { formData } = state.interaction;
  const { messages } = state.chat;
  const interactionId = state.interaction.interactionId;

  // Build conversation history for context
  const conversationHistory = messages.slice(-10).map((m) => ({
    role: m.role,
    content: m.content,
  }));

  const response = await sendChatMessage({
    message,
    conversation_history: conversationHistory,
    current_form_data: formData,
    interaction_id: interactionId,
  });

  // If the agent returned form data, update the Redux store
  if (response.form_data) {
    dispatch(setFormData(response.form_data as any));
    if (response.updated_fields && response.updated_fields.length > 0) {
      dispatch(setHighlightedFields(response.updated_fields));
    }
  }

  // Update interaction ID if returned
  if (response.interaction_id) {
    dispatch(setInteractionId(response.interaction_id));
  }

  return response;
});

const chatSlice = createSlice({
  name: "chat",
  initialState,
  reducers: {
    /** Add a user message to the chat. */
    addUserMessage(state, action: PayloadAction<ChatMessage>) {
      state.messages.push(action.payload);
    },

    /** Clear chat history. */
    clearChat(state) {
      state.messages = [];
      state.error = null;
      state.currentTool = null;
    },

    /** Set current tool being used. */
    setCurrentTool(state, action: PayloadAction<string | null>) {
      state.currentTool = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(sendMessage.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(sendMessage.fulfilled, (state, action) => {
        state.isLoading = false;
        state.currentTool = action.payload.tool_used;

        // Add AI response message
        const aiMessage: ChatMessage = {
          id: `ai-${Date.now()}`,
          role: "assistant",
          content: action.payload.ai_message,
          toolUsed: action.payload.tool_used,
          timestamp: new Date().toISOString(),
          updatedFields: action.payload.updated_fields,
        };
        state.messages.push(aiMessage);
      })
      .addCase(sendMessage.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || "Something went wrong";

        // Add error message
        const errorMsg: ChatMessage = {
          id: `err-${Date.now()}`,
          role: "assistant",
          content: "⚠️ Sorry, I encountered an error processing your request. Please try again.",
          toolUsed: null,
          timestamp: new Date().toISOString(),
        };
        state.messages.push(errorMsg);
      });
  },
});

export const { addUserMessage, clearChat, setCurrentTool } = chatSlice.actions;
export default chatSlice.reducer;
