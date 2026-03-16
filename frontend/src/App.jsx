import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AuthContextProvider } from './contexts/AuthContext'
import Layout from './components/Layout'
import ProtectedRoute from './components/ProtectedRoute'
import HomePage from './pages/HomePage'
import Login from './pages/Login'
import Signup from './pages/Signup'
import ForgotPassword from './pages/ForgotPassword'
import ResumeAnalysis from './pages/ResumeAnalysis'
import AIInterview from './pages/AIInterview'
import CareerInsights from './pages/CareerInsights'
import JobMatching from './pages/JobMatching'

function App() {
  return (
    <AuthContextProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route
            path="/*"
            element={
              <Layout>
                <Routes>
                  <Route path="/" element={<HomePage />} />
                  <Route
                    path="/resume"
                    element={
                      <ProtectedRoute>
                        <ResumeAnalysis />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/interview"
                    element={
                      <ProtectedRoute>
                        <AIInterview />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/career"
                    element={
                      <ProtectedRoute>
                        <CareerInsights />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/jobs"
                    element={
                      <ProtectedRoute>
                        <JobMatching />
                      </ProtectedRoute>
                    }
                  />
                </Routes>
              </Layout>
            }
          />
        </Routes>
      </BrowserRouter>
    </AuthContextProvider>
  )
}

export default App

