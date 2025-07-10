import Lottie from 'lottie-react';
import animationData from '../assets/eval.json'; 
import { Link } from "react-router-dom";
import '../styles/home.css'; 

function Home() {
  return (
    <div className="home-container">
      <div className="text-section">
        <h1>Welcome to Auto Agent Evaluation!</h1>
        <p>Evaluate and optimize agent performance in 4 easy steps:</p>

        <ol className="evaluation-steps">
        <li>Identify agents to be evaluated</li>
        <li>Define evaluation criteria (roles)</li>
        <li>Upload supporting documentation</li>
        <li>Review and finalize evaluations</li>
        <li>Assign agents to tasks with specified requirements</li>
        <li>Optimize your team through Role-Based Collaboration</li>
        </ol>
        

        <Link to="/agents" className="start-link">
            <button className="start-button">Get Started</button>
        </Link>
      </div>

      <div className="animation-section">
        <Lottie animationData={animationData} loop={true} speed={0.5} />
      </div>
    </div>
  );
}

export default Home;