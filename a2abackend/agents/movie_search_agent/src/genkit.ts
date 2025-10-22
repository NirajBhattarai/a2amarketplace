import { genkit } from "genkit";
import { googleAI } from "@genkit-ai/googleai";

// Configure Genkit with Google AI
export const ai = genkit({
  plugins: [
    googleAI({
      apiKey: process.env.GEMINI_API_KEY || "demo-key",
    }),
  ],
});