import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import AuthProvider from './routes/AuthContext';
import Login from './components/Login';
import ProtectedRoute from './routes/Protected';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          {/* <Route
            path="/"
            element={
              <ProtectedRoute>
               <p>Welcome to pod-club</p>
              </ProtectedRoute>
            }
          /> */}
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
