import Personalization from "../NutriAIFinal/src/components/Personalization";
import OpenAI from "openai";

const openai = new OpenAI({  apiKey: process .env.OPENAI_API_KEY  });

const response = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
        { role: "system", content: "You are a nutrition coach." },
        { role: "user", content: "Create a 2200 calarie muscle gain plan." }
    ]
});
function calculateCalories(tdee, goal) {
    if (goal === "fat_loss") return tdee - 500;
    if (goal === "muscle_gain") return tdee + 300;
    return tdee;
}

function detectExtremeCalories