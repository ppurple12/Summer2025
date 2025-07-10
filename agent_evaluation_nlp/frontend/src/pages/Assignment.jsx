import { Link } from "react-router-dom";
import "../styles/assignment.css"; // optional if you separate CSS

function AssignmentPage() {
  return (
    <div >
      <h2>Assignment</h2>
      <div className="text-section">
        <p className="text">Please choose the type of assignment below:</p>

        <div className="assignment-options">
          <div className="assignment-box">
            <h3>GRA</h3>
            <p>Group Role Assignment (GRA) aims to maximize group performance. In GRA, each agent is assigned a singular role 
              within the group. To receive a optimized agent assignment, you must provide a role range for each role.</p>
            <Link to="GRA1">
              <button className="start-button">GRA</button>
            </Link>
          </div>

          <div className="assignment-box">
            <h3>GMRA</h3>
            <p>Group Multi-Role Assignment (GMRA) aims to maximize group performance. In GMRA, each agent can be assigned multiple roles
              within the group. To receive a optimized agent assignment, you must provide a role range for each role and agent constraints.</p>
            <Link to="GMRA1">
              <button className="start-button">GMRA</button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AssignmentPage;