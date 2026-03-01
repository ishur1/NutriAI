import { useState } from 'react';
import NutriAiLogo from '../assets/NutriAI.png';

function Personalization() {
  // Local form state for user nutrition preferences.
  const [formData, setFormData] = useState({
    name: '',
    goal: 'maintain',
    dietaryPreference: 'none',
    activityLevel: 'moderate',
    mealsPerDay: 3,
  });

  const handleChange = (event) => {
    const { name, value } = event.target;
    // Keep all fields controlled; convert mealsPerDay to number for backend consistency.
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'mealsPerDay' ? Number(value) : value,
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    // Send profile preferences to backend API.
    const res = await fetch("http://localhost:5000/api/profile", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formData),
    });

    // Backend returns JSON with { ok, ... }.
    const data = await res.json();
    console.log(data);

    // Basic user feedback based on backend result.
    if (data.ok) alert("Saved to backend!");
    else alert("Error: " + data.error);
  };

  return (
    <section className="personalization-card">
      <h1>NutriAI Personalization</h1>
      {/* Controlled form: each input reads/writes the formData state. */}
      <form className="personalization-form" onSubmit={handleSubmit}>
        <label>
          Name
          <input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleChange}
            required
          />
        </label>

        <label>
          Goal
          <select name="goal" value={formData.goal} onChange={handleChange}>
            <option value="lose">Lose</option>
            <option value="maintain">Maintain</option>
            <option value="gain">Gain</option>
          </select>
        </label>

        <label>
          Dietary Preference
          <select
            name="dietaryPreference"
            value={formData.dietaryPreference}
            onChange={handleChange}
          >
            <option value="none">No Preference</option>
            <option value="vegetarian">Vegetarian</option>
            <option value="vegan">Vegan</option>
            <option value="keto">Keto</option>
            <option value="paleo">Paleo</option>
          </select>
        </label>

        <label>
          Activity Level
          <select
            name="activityLevel"
            value={formData.activityLevel}
            onChange={handleChange}
          >
            <option value="sedentary">Sedentary</option>
            <option value="light">Light</option>
            <option value="moderate">Moderate</option>
            <option value="active">Active</option>
            <option value="very-active">Very Active</option>
          </select>
        </label>

        <label>
          Meals Per Day
          <input
            type="number"
            name="mealsPerDay"
            min="1"
            max="10"
            value={formData.mealsPerDay}
            onChange={handleChange}
            required
          />
        </label>

        <button type="submit">Save Preferences</button>
      </form>
    </section>
  );
}

export default Personalization;
