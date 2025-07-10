import { useEffect, useState } from "react";
import axios from "axios";
import { Trash } from "lucide-react";
import { Link } from "react-router-dom";
import "../styles/agent.css";

const RolesPage = ({userId}) => {
  const [roles, setRoles] = useState([]); // raw flat roles list from backend
  const [groupedRoles, setGroupedRoles] = useState([]); // grouped roles as state
  const [showAddForm, setShowAddForm] = useState(false);
  const [newRole, setNewRole] = useState({ roleName: "", keywords: "" });
  const [loading, setLoading] = useState(false);
  const [newKeywords, setNewKeywords] = useState({}); // { roleName: "keyword" }

  // Helper function: group roles by ROLE_NAME and collect ROLE_KEYWORDs into arrays
  const groupRoles = (rolesList) => {
    const grouped = rolesList.reduce((acc, { ROLE_NAME, ROLE_KEYWORD }) => {
      if (!acc[ROLE_NAME]) acc[ROLE_NAME] = new Set(); // Use Set for uniqueness, optional
      acc[ROLE_NAME].add(ROLE_KEYWORD);
      return acc;
    }, {});
     
    return Object.entries(grouped).map(([roleName, keywordsSet]) => ({
      roleName,
      keywords: Array.from(keywordsSet),
    }));
  };

  // Load roles on mount
  useEffect(() => {
    axios.get(`/api/roles/${userId}`)
      .then((res) => {
        const data = Array.isArray(res.data) ? res.data : [];
        setRoles(data);
        setGroupedRoles(groupRoles(data));
      })
      .catch((err) => {
        console.error("Failed to fetch roles", err);
        setRoles([]);
        setGroupedRoles([]);
      });
  }, []);

  const handleAddRoleClick = () => setShowAddForm(true);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNewRole(prev => ({ ...prev, [name]: value }));
  };

  const handleKeywordChange = (roleName, e) => {
    const value = e.target.value;
    setNewKeywords(prev => ({ ...prev, [roleName]: value }));
  };


  const handleAddRoleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const keywords = newRole.keywords
        .split(",")
        .map(k => k.trim())
        .filter(k => k);

      // Send all keywords in one POST payload
      const payload = {
        ROLE_NAME: newRole.roleName,
        ROLE_KEYWORDS: keywords  // array, not string
      };
      console.log(payload)
      const res = await axios.post(`/api/roles/${userId}`, payload);

      // res.data is expected to be an array of created roles
      const newRoles = res.data;

      const updatedRoles = [...roles, ...newRoles];
      setRoles(updatedRoles);
      setGroupedRoles(groupRoles(updatedRoles));

      setNewRole({ roleName: "", keywords: "" });
      setShowAddForm(false);
    } catch (err) {
      console.error("Failed to add role", err);
      alert("Failed to add role. Check console for details.");
    } finally {
      setLoading(false);
    }
  };

  const handleAddKeywordForRole = async (roleName) => {
    setLoading(true);
    const keyword = newKeywords[roleName];

    if (!keyword) return alert("Enter a keyword");

    try {
      const payload = { ROLE_NAME: roleName, ROLE_KEYWORD: keyword };
      const res = await axios.post(`/api/keyword/${userId}`, payload);
      const addedKeyword = res.data;

      const updatedRoles = [...roles, addedKeyword];
      setRoles(updatedRoles);
      setGroupedRoles(groupRoles(updatedRoles));
      setNewKeywords(prev => ({ ...prev, [roleName]: "" }));
      // update roles state here
    } catch (err) {
      console.error(err);
      alert("Failed to add keyword");
    }
    finally {
      setLoading(false);
    }
  };

  const handleDeleteRole = async (roleName) => {
    if (!window.confirm(`Delete the role "${roleName}" and all its keywords? Doing so removes this role from evaluation.`)) return;
    try {
      await axios.delete(`/api/roles/${encodeURIComponent(roleName)}?userId=${userId}`);
      setGroupedRoles(prev => {
        const copy = {...prev};
        delete copy[roleName];
        window.location.reload();
      });
    } 
    catch (err) {
      console.error("Failed to delete role", err);
    }
    finally {
      setLoading(false);
    }
  };

  return (
    <div className="agent-container">
      <h2>Roles</h2>
      <div>
          <p className="text">
            Press Add New Roles to add roles into consideration. Consider adding keywords to optimize the evaluation.
            <br></br>
            Ex: Role: Public Speaking - Keywords: articulate, fluent, persuasive
          </p>
        </div>
      {groupedRoles.length > 0 ? (
        groupedRoles.map(({ roleName, keywords }) => (
          <div key={roleName} className="agent-card">
            <div className="agent-info">
              <p className="agent-name">{roleName}</p>
              <p className="agent-keywords">
                Keywords: {keywords.join(", ")}
              </p>
            </div >
            <form onSubmit={handleAddRoleSubmit} className="add-agent-form" style={{ marginTop: "1rem" }}>
              <input
                type="text"
                name="keywords"
                placeholder="Add a new keyword"
                value={newKeywords[roleName] || ""}
                onChange={(e) => handleKeywordChange(roleName, e)}
                required
              />
              <button onClick={() => handleAddKeywordForRole(roleName)} disabled={loading} className="add-agent-button">
                {loading ? "Adding..." : "Add Keyword"}
              </button>
              <button
                onClick={() => handleDeleteRole(roleName)}
                className="delete-button"
                title="Delete role"
              >
                
                <Trash size={20} className="trash-icon" />
              </button>
            </form>
            
          </div>
        ))
      ) : (
        
        <h2 className="text">No roles added.</h2>
      )}


      {showAddForm ? (
        <form onSubmit={handleAddRoleSubmit} className="add-agent-form" style={{ marginTop: "1rem" }}>
          <input
            type="text"
            name="roleName"
            placeholder="Role Name"
            value={newRole.roleName}
            onChange={handleInputChange}
            required
          />
          <input
            type="text"
            name="keywords"
            placeholder="Keywords (comma-separated)"
            value={newRole.keywords}
            onChange={handleInputChange}
          />
          <button type="submit" disabled={loading}>
            {loading ? "Adding..." : "Add Role"}
          </button>
          <button type="button" onClick={() => setShowAddForm(false)} disabled={loading}>
            Cancel
          </button>
        </form>
      ) : (
        <button onClick={handleAddRoleClick} className="add-agent-button" style={{ marginTop: "1rem" }}>
          Add New Role
        </button>
      )}
      <div className="spacer" />
        <Link to="/documents" className="button-container">
          <button className="proceed-button"> Proceed to Document Upload </button>
        </Link>
    </div>
  );
};

export default RolesPage;
