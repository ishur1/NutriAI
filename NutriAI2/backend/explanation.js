const functions = require("firebase-functions");
const admin = require("firebase-admin");
const OpenAI = require("openai");

if (!admin.apps.length) {
  admin.initializeApp();
}

exports.chatCompletion = functions.https.onCall(async (data, context) => {
  const prompt = (data?.prompt || "").trim();
  if (!prompt) {
    throw new functions.https.HttpsError(
      "invalid-argument",
      "Missing required field: prompt"
    );
  }

  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) {
    throw new functions.https.HttpsError(
      "failed-precondition",
      "Server is missing OPENAI_API_KEY"
    );
  }

  const openai = new OpenAI({ apiKey });

  try {
    const completion = await openai.chat.completions.create({
      model: "gpt-4.1-mini",
      messages: [
        {
          role: "system",
          content:
            "You are a nutrition AI. Explain clearly why the nutrition-scoring algorithm made its decision from scanned food nutrition values.",
        },
        { role: "user", content: prompt },
      ],
      temperature: 0.3,
    });

    const aiResponse = completion.choices?.[0]?.message?.content?.trim() || "";

    return { aiResponse };
  } catch (error) {
    console.error("OpenAI request failed:", error);
    throw new functions.https.HttpsError(
      "internal",
      "Failed to generate explanation"
    );
  }
});
