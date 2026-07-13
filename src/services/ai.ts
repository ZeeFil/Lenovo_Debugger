import { GoogleGenAI } from "@google/genai";

/**
 * Modifies the Sway configuration using Gemini AI based on a user prompt.
 */
export const generateSwayConfig = async (apiKey: string, currentConfig: string, promptText: string): Promise<string> => {
  if (!apiKey) throw new Error("API key is required");
  if (!currentConfig) throw new Error("Current configuration is empty");

  const ai = new GoogleGenAI({ apiKey });
  
  const prompt = `You are an expert Linux system administrator configuring sway for a Lenovo Duet 2. 
Current config:
${currentConfig}

User request: ${promptText}

Return ONLY the new full valid configuration file text. Do not include markdown formatting backticks if possible, just the raw config.`;

  const response = await ai.models.generateContent({
    model: "gemini-3.5-flash",
    contents: prompt
  });

  let newConfig = response.text || "";
  // Strip any markdown blocks if the model includes them anyway
  newConfig = newConfig.replace(/^\s*```[a-z]*\n/im, '').replace(/\n```\s*$/im, '').trim();
  
  return newConfig;
};
