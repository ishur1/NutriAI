import NutriAILogo from './assets/NutriAI.png'
import './App.css'

function App() {
  return (
    <>
      <div>
        Vite logo
        <a href="https://react.dev" target="_blank">
          <img src={NutriAILogo} className="logo Nutri" alt="NutriAILogo" />
        </a>
      </div>
      <h1>Vite + React</h1>
      <div className="card">
        <p>
          Edit <code>src/App.tsx</code> and save to test HMR
        </p>
      </div>
      <p className="read-the-docs">
        Click on the Vite and React logos to learn more
      </p>
    </>
  )
}

export default App
