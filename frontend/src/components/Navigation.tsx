import { useNavigate, useLocation } from 'react-router-dom'
import { useTheme } from '@/context/ThemeContext'
import { useAuthStore } from '@/stores/authStore'

export default function Navigation() {
  const navigate = useNavigate()
  const location = useLocation()
  const { theme } = useTheme()
  const { user } = useAuthStore()

  const isActive = (path: string) => location.pathname === path

  const navItems = [
    { path: '/dashboard', label: '仪表盘' },
    { path: '/goals', label: '目标' },
    { path: '/tasks', label: '任务' },
    { path: '/achievements', label: '成就' },
    { path: '/analytics', label: '分析' },
  ]

  // 只有管理员才显示管理菜单
  if (user?.is_admin) {
    navItems.push({ path: '/admin', label: '管理' })
  }

  return (
    <nav className="bg-white shadow-sm sticky top-[68px] z-40 border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-start items-center h-12 overflow-x-auto scrollbar-hide">
          {navItems.map((item) => (
            <button
              key={item.path}
              onClick={() => navigate(item.path)}
              className={`px-5 py-2 font-semibold text-sm whitespace-nowrap transition duration-200 rounded-lg flex-shrink-0 mr-1 ${
                isActive(item.path)
                  ? `${theme.navActiveBg} ${theme.navActiveText} border-b-2 ${theme.navActiveBorder}`
                  : `text-gray-600 ${theme.navHoverText} hover:bg-gray-50`
              }`}
            >
              {item.label}
            </button>
          ))}
        </div>
      </div>
    </nav>
  )
}
