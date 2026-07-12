import express from "express";
import path from "path";
import { createServer as createViteServer } from "vite";
import { GoogleGenAI } from "@google/genai";

const app = express();
const PORT = 3000;

app.use(express.json());

app.post("/api/diagnose", async (req, res) => {
  try {
    const { logs } = req.body;
    if (!logs) {
      return res.status(400).json({ error: "No logs provided." });
    }

    const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });
    const response = await ai.models.generateContent({
      model: "gemini-3.5-flash",
      contents: `You are an expert Linux system administrator (specifically postmarketOS sway edition on a Lenovo Duet 2 tablet). Analyze the following terminal output/logs and provide a brief, actionable diagnostic summary and suggest any commands to fix potential issues. Keep it concise.

Terminal Logs:
${logs}
`,
    });

    res.json({ analysis: response.text });
  } catch (error: any) {
    console.error("Diagnostic error:", error);
    res.status(500).json({ error: error.message || "Failed to analyze logs." });
  }
});

async function startServer() {
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), "dist");
    app.use(express.static(distPath));
    app.get("*", (req, res) => {
      res.sendFile(path.join(distPath, "index.html"));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Server running on port ${PORT}`);
  });
}

startServer();
