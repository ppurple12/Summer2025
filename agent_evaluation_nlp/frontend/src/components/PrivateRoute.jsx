import { Navigate } from 'react-router-dom';
import { useAuth } from './AuthContext';

export default function PrivateRoute({ children }) {
  const { userId } = useAuth();

  if (!userId || userId < 0) {
    return <Navigate to="/login" replace />;
  }
  return children;
}