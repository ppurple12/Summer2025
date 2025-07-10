import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

import Header from "./components/Header";
import Footer from "./components/Footer";
import Agents from "./pages/Agents";
import Roles from "./pages/Roles";
import Documents from "./pages/Documents";
import Evaluation from "./pages/Evaluation";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Account from "./pages/Account";
import Assignment from "./pages/Assignment";
import GRA1 from "./pages/assignments/GRA_1";
import GRA2 from "./pages/assignments/GRA_2";
import GMRA1 from "./pages/assignments/GMRA_1";
import GMRA2 from "./pages/assignments/GMRA_2";
import GMRA3 from "./pages/assignments/GMRA_3";
import PrivateRoute from './components/PrivateRoute';
import AgentStatuses from "./pages/assignments/Agent_statuses"
import { useAuth } from './components/AuthContext';



function App() {

   const { userId } = useAuth();

  return (
    <Router>
      <div className="app-wrapper">
        <Header />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Home userId={userId}/>} />
            <Route path="/login" element={<Login />} />


            <Route
              path="/agents"
              element={ <PrivateRoute> <Agents userId={userId}/> </PrivateRoute>}
            />
            <Route
              path="/agent_statuses"
              element={ <PrivateRoute> <AgentStatuses userId={userId}/> </PrivateRoute>}
            />
            <Route
              path="/roles"
              element={<PrivateRoute> <Roles userId={userId}/> </PrivateRoute>}
            />
            <Route
              path="/documents"
              element={<PrivateRoute> <Documents userId={userId}/> </PrivateRoute>}
            />
            <Route
              path="/evaluation"
              element={ <PrivateRoute> <Evaluation userId={userId}/> </PrivateRoute>}
            />
            <Route
              path="/account"
              element={ <PrivateRoute> <Account userId={userId}/> </PrivateRoute>}
            />
            <Route
              path="/assignment"
              element={ <PrivateRoute> <Assignment userId={userId}/> </PrivateRoute>}
            />
            <Route
              path="/assignment/GRA1"
              element={ <PrivateRoute> <GRA1 userId={userId}/> </PrivateRoute>}
            />
            <Route
              path="/assignment/GRA2/:userId"
              element={<PrivateRoute> <GRA2 /> </PrivateRoute>}
            />
            <Route
              path="/assignment/GMRA1"
              element={ <PrivateRoute> <GMRA1 userId={userId}/> </PrivateRoute>}
            />
            <Route
              path="/assignment/GMRA2/:userId"
              element={<PrivateRoute> <GMRA2 /> </PrivateRoute>}
            />
            <Route
              path="/assignment/GMRA3/:userId"
              element={<PrivateRoute> <GMRA3 /> </PrivateRoute>}
            />
          </Routes>
        </main>
        <Footer />
      </div>
    </Router>
  );
}

export default App;