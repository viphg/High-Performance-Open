import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './stores/authStore'
import { ToastProvider } from './context/ToastContext'
import { ThemeProvider } from './context/ThemeContext'
import Header from './components/Header'
import Navigation from './components/Navigation'
import './styles/index.css'

// Pages
import LoginPage from './pages/auth/Login'
import RegisterPage from './pages/auth/Register'
import Dashboard from './pages/dashboard/Dashboard'
import GoalsPage from './pages/dashboard/Goals'
import GoalDetailPage from './pages/dashboard/GoalDetail'
import TasksPage from './pages/dashboard/Tasks'
import TaskDetailPage from './pages/dashboard/TaskDetail'
import AchievementsPage from './pages/dashboard/Achievements'
import AnalyticsPage from './pages/dashboard/Analytics'
import ProfilePage from './pages/Profile'
import NotificationsPage from './pages/Notifications'
import NotificationSettings from './pages/NotificationSettings'
import AdminDashboard from './pages/admin/AdminDashboard'
import UserManagement from './pages/admin/UserManagement'

// Protected Route Component
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore()

  if (!isAuthenticated) {
    return <Navigate to="/auth/login" replace />
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <Header />
      <Navigation />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        {children}
      </main>
    </div>
  )
}

function App() {
  const { isAuthenticated } = useAuthStore()

  return (
    <ThemeProvider>
      <ToastProvider>
        <Router>
          <Routes>
            {/* Auth Routes */}
            <Route path="/auth/login" element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <LoginPage />} />
            <Route path="/auth/register" element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <RegisterPage />} />

            {/* Protected Routes */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />
        
            <Route
              path="/goals"
              element={
                <ProtectedRoute>
                  <GoalsPage />
                </ProtectedRoute>
              }
            />

            <Route
              path="/goals/:id"
              element={
                <ProtectedRoute>
                  <GoalDetailPage />
                </ProtectedRoute>
              }
            />
        
            <Route
              path="/tasks"
              element={
                <ProtectedRoute>
                  <TasksPage />
                </ProtectedRoute>
              }
            />

            <Route
              path="/tasks/:id"
              element={
                <ProtectedRoute>
                  <TaskDetailPage />
                </ProtectedRoute>
              }
            />

            <Route
              path="/achievements"
              element={
                <ProtectedRoute>
                  <AchievementsPage />
                </ProtectedRoute>
              }
            />

            <Route
              path="/analytics"
              element={
                <ProtectedRoute>
                  <AnalyticsPage />
                </ProtectedRoute>
              }
            />

            <Route
              path="/profile"
              element={
                <ProtectedRoute>
                  <ProfilePage />
                </ProtectedRoute>
              }
            />

            {/* Notification Routes */}
            <Route
              path="/notifications"
              element={
                <ProtectedRoute>
                  <NotificationsPage />
                </ProtectedRoute>
              }
            />

            <Route
              path="/settings/notifications"
              element={
                <ProtectedRoute>
                  <NotificationSettings />
                </ProtectedRoute>
              }
            />

            {/* Admin Routes */}
            <Route
              path="/admin"
              element={
                <ProtectedRoute>
                  <AdminDashboard />
                </ProtectedRoute>
              }
            />

            <Route
              path="/admin/users"
              element={
                <ProtectedRoute>
                  <UserManagement />
                </ProtectedRoute>
              }
            />

            {/* Default Redirect */}
            <Route path="/" element={<Navigate to="/auth/login" replace />} />
            <Route path="*" element={<Navigate to="/auth/login" replace />} />
          </Routes>
        </Router>
      </ToastProvider>
    </ThemeProvider>
  )
}

export default App
