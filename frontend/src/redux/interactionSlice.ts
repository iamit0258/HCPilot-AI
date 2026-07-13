/**
 * Interaction Redux slice — manages the CRM form state.
 * The form is READ-ONLY for the user; only AI actions dispatch updates.
 */
import { createSlice } from "@reduxjs/toolkit";
import type { PayloadAction } from "@reduxjs/toolkit";
import type { InteractionFormData, InteractionState } from "../types";
import { EMPTY_FORM } from "../types";

const initialState: InteractionState = {
  formData: { ...EMPTY_FORM },
  interactionId: null,
  highlightedFields: [],
  isNew: true,
};

const interactionSlice = createSlice({
  name: "interaction",
  initialState,
  reducers: {
    /** Replace entire form data (used by log_interaction tool). */
    setFormData(state, action: PayloadAction<InteractionFormData>) {
      state.formData = action.payload;
      state.isNew = false;
    },

    /** Update specific fields only (used by edit_interaction tool). */
    updateFields(state, action: PayloadAction<Partial<InteractionFormData>>) {
      state.formData = { ...state.formData, ...action.payload };
    },

    /** Set the active interaction ID. */
    setInteractionId(state, action: PayloadAction<number | null>) {
      state.interactionId = action.payload;
    },

    /** Highlight fields that were just updated by AI. */
    setHighlightedFields(state, action: PayloadAction<string[]>) {
      state.highlightedFields = action.payload;
    },

    /** Clear all highlights after animation completes. */
    clearHighlights(state) {
      state.highlightedFields = [];
    },

    /** Reset form to empty state. */
    clearForm(state) {
      state.formData = { ...EMPTY_FORM };
      state.interactionId = null;
      state.highlightedFields = [];
      state.isNew = true;
    },
  },
});

export const {
  setFormData,
  updateFields,
  setInteractionId,
  setHighlightedFields,
  clearHighlights,
  clearForm,
} = interactionSlice.actions;

export default interactionSlice.reducer;
