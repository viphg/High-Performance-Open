import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import { useTheme } from '@/context/ThemeContext'
import type { ThemeType } from '@/context/ThemeContext'

const themeOptions: { value: ThemeType; label: string; icon: string }[] = [
  { value: 'indigo', label: '靛蓝', icon: '💜' },
  { value: 'green', label: '绿色', icon: '💚' },
  { value: 'blue', label: '蓝色', icon: '💙' },
  { value: 'orange', label: '橙色', icon: '🧡' },
  { value: 'rose', label: '玫瑰', icon: '💗' },
]

export default function Header() {
  const navigate = useNavigate()
  const { user, logout } = useAuthStore()
  const { theme, themeType, setTheme } = useTheme()
  const [showThemeMenu, setShowThemeMenu] = useState(false)
  const [showProfileMenu, setShowProfileMenu] = useState(false)
  const themeRef = useRef<HTMLDivElement>(null)
  const profileRef = useRef<HTMLDivElement>(null)

  // 点击外部关闭下拉菜单
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (themeRef.current && !themeRef.current.contains(e.target as Node)) {
        setShowThemeMenu(false)
      }
      if (profileRef.current && !profileRef.current.contains(e.target as Node)) {
        setShowProfileMenu(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleLogout = () => {
    logout()
    navigate('/auth/login')
  }

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)
  }

  const currentTheme = themeOptions.find((t) => t.value === themeType)

  return (
    <header className={`${theme.headerGradient} shadow-lg sticky top-0 z-50`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-5 flex justify-between items-center">
        <div className="cursor-pointer" onClick={() => navigate('/dashboard')}>
          <h1 className="text-3xl font-bold text-white hover:text-white/80 transition">High-Performance</h1>
          <p className="text-white/70 mt-1 text-sm">个人成长管理平台</p>
        </div>

        <div className="flex items-center space-x-4">
          {/* Theme Selector */}
          <div className="relative" ref={themeRef}>
            <button
              onClick={() => setShowThemeMenu(!showThemeMenu)}
              className="bg-white/20 text-white px-4 py-2 rounded-full hover:bg-white/30 transition flex items-center space-x-2 font-medium text-sm backdrop-blur-sm"
            >
              <span>{currentTheme?.icon}</span>
              <span>{currentTheme?.label}</span>
            </button>
            {showThemeMenu && (
              <div className="absolute right-0 mt-2 w-44 bg-white rounded-xl shadow-xl border border-gray-100 overflow-hidden animate-fade-in">
                {themeOptions.map((opt) => (
                  <button
                    key={opt.value}
                    onClick={() => {
                      setTheme(opt.value)
                      setShowThemeMenu(false)
                    }}
                    className={`w-full px-4 py-3 text-left font-semibold flex items-center space-x-2 transition text-sm ${
                      themeType === opt.value
                        ? `${theme.dropdownActiveBg} ${theme.dropdownActiveText}`
                        : 'text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    <span>{opt.icon}</span>
                    <span>{opt.label}</span>
                    {themeType === opt.value && <span className="ml-auto text-xs">✓</span>}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Profile Menu */}
          <div className="relative" ref={profileRef}>
            <button
              onClick={() => setShowProfileMenu(!showProfileMenu)}
              className="w-10 h-10 bg-white/20 text-white rounded-full flex items-center justify-center hover:bg-white/30 transition font-bold text-sm border-2 border-white/30 backdrop-blur-sm"
            >
              {getInitials(user?.full_name || user?.username || 'U')}
            </button>
            {showProfileMenu && (
              <div className="absolute right-0 mt-2 w-52 bg-white rounded-xl shadow-xl border border-gray-100 overflow-hidden animate-fade-in">
                <div className={`px-4 py-3 bg-gradient-to-r ${theme.profileBg} border-b border-gray-100`}>
                  <p className="text-sm font-bold text-gray-800">{user?.full_name || user?.username}</p>
                  <p className="text-xs text-gray-600 mt-1">{user?.email}</p>
                </div>
                <button
                  onClick={() => {
                    navigate('/profile')
                    setShowProfileMenu(false)
                  }}
                  className="w-full px-4 py-3 text-left font-semibold text-gray-700 hover:bg-gray-50 transition flex items-center space-x-2 text-sm"
                >
                  <span>个人资料</span>
                </button>
                <button
                  onClick={handleLogout}
                  className="w-full px-4 py-3 text-left font-semibold text-red-600 hover:bg-red-50 transition flex items-center space-x-2 border-t border-gray-100 text-sm"
                >
                  <span>登出</span>
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}
