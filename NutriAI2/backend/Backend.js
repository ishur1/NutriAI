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

function detectExtremeCalories ({
    gender,
    tdee,
    proposedCalories
})  {
   const minCalories = gender === "female" ? 1200 : 1500;

   const deficitPercent = ((tdee - proposedCalories) / tdee) * 100;
   const surplusPercent = ((proposedCalories - tdee) / tdee) * 100;

   let warnings = []
   let blocked = false;


   if (proposedCalories < minCalories) {
    blocked = true;
    warnings.push("Calorie target below evidence-based minimum.");
   }


   if (deficitPercent > 25) {
    warnings.push("Deficit exceeds recommended 25% maximum.");
   }


   if (surplusPercent > 15) {
    warnings.push("Surplus exceeds recommended 15% maximum.");
   }

   return {
    approved: !blocked,
    blocked,
    warnings
   };
}

function adjustCaloriesForGoal({ tdee, goal, aggressiveness = "moderate" }) {
    let adjustmentPercent = 0;
  
    if (goal === "fat_loss") {
      if (aggressiveness === "mild") adjustmentPercent = -0.10;
      if (aggressiveness === "moderate") adjustmentPercent = -0.20;
      if (aggressiveness === "aggressive") adjustmentPercent = -0.25;
    }
  
    if (goal === "muscle_gain") {
      if (aggressiveness === "mild") adjustmentPercent = 0.05;
      if (aggressiveness === "moderate") adjustmentPercent = 0.10;
      if (aggressiveness === "aggressive") adjustmentPercent = 0.15;
    }
  
    if (goal === "maintenance") {
      adjustmentPercent = 0;
    }
  
    const targetCalories = Math.round(tdee * (1 + adjustmentPercent));
  
    return {
      targetCalories,
      adjustmentPercent
    };
  }

  function calculateMacros({ weightKg, targetCalories }) {
    const proteinGrams = Math.round(weightKg * 2); // 2g/kg
    const proteinCalories = proteinGrams * 4;
  
    const fatCalories = targetCalories * 0.25;
    const fatGrams = Math.round(fatCalories / 9);
  
    const remainingCalories = targetCalories - proteinCalories - fatCalories;
    const carbGrams = Math.round(remainingCalories / 4);
  
    return {
      proteinGrams,
      fatGrams,
      carbGrams
    };
  }

  function filterMeals(meals, preferences) {
    return meals.filter(meal => {
        return preferences.every(pref => meal.tags.includes(pref));
    });
  }
  
  