import { useEffect, useState } from "react";
import axios from "axios";

const Account = ({userId}) => {
    const [profile, setProfile] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        axios.get(`/api/account/${userId}`)
        .then(response => {
            setProfile(response.data);
            setError(null);
        })
        .catch(err => {
            console.error("Error loading profile:", err);
            setError("Failed to load profile.");
            setProfile(null);
        })
        .finally(() => setLoading(false));
    }, [userId]);

    if (loading) return <p>Loading profile...</p>;
    if (error) return <p className="text">{error}</p>;
    if (!profile) return <p className="text">No profile data found.</p>;

    return (
        <div className="agents-container">
        <h2>User Profile</h2>

        <div className="agent-card" style={{ flexDirection: 'column', alignItems: 'flex-start' }}>
            <p><strong>First Name:</strong> {profile.FIRST_NAME}</p>
            <p><strong>Last Name:</strong> {profile.LAST_NAME}</p>
            <p><strong>Email:</strong> {profile.USER_EMAIL}</p>
            <p><strong>Company Name:</strong> {profile.COMPANY_NAME || 'N/A'}</p>
            <p><strong>Department:</strong> {profile.COMPANY_DEPARTMENT || 'N/A'}</p>
            <p><strong>Position:</strong> {profile.COMPANY_POSITION || 'N/A'}</p>
        </div>
        </div>
    );
    };
export default Account;