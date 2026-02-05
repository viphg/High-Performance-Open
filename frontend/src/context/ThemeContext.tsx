import React, { createContext, useContext, useState, useEffect } from 'react'

export type ThemeType = 'indigo' | 'green' | 'blue' | 'orange' | 'rose'

interface ThemeConfig {
  name: ThemeType
  headerGradient: string
  navActiveBg: string
  navActiveBorder: string
  navActiveText: string
  navHoverText: string
  dropdownActiveBg: string
  dropdownActiveText: string
  profileBg: string
}

const themes: Record<ThemeType, ThemeConfig> = {
  indigo: {
    name: 'indigo',
    headerGradient: 'bg-gradient-to-r from-indigo-600 to-purple-600',
    navActiveBg: 'bg-gradient-to-b from-indigo-50 to-transparent',
    navActiveBorder: 'border-indigo-600',
    navActiveText: 'text-indigo-700',
    navHoverText: 'hover:text-indigo-600',
    dropdownActiveBg: 'bg-indigo-100',
    dropdownActiveText: 'text-indigo-700',
    profileBg: 'from-indigo-50 to-purple-50',
  },
  green: {
    name: 'green',
    headerGradient: 'bg-gradient-to-r from-green-600 to-emerald-600',
    navActiveBg: 'bg-gradient-to-b from-green-50 to-transparent',
    navActiveBorder: 'border-green-600',
    navActiveText: 'text-green-700',
    navHoverText: 'hover:text-green-600',
    dropdownActiveBg: 'bg-green-100',
    dropdownActiveText: 'text-green-700',
    profileBg: 'from-green-50 to-emerald-50',
  },
  blue: {
    name: 'blue',
    headerGradient: 'bg-gradient-to-r from-blue-600 to-cyan-600',
    navActiveBg: 'bg-gradient-to-b from-blue-50 to-transparent',
    navActiveBorder: 'border-blue-600',
    navActiveText: 'text-blue-700',
    navHoverText: 'hover:text-blue-600',
    dropdownActiveBg: 'bg-blue-100',
    dropdownActiveText: 'text-blue-700',
    profileBg: 'from-blue-50 to-cyan-50',
  },
  orange: {
    name: 'orange',
    headerGradient: 'bg-gradient-to-r from-orange-600 to-red-600',
    navActiveBg: 'bg-gradient-to-b from-orange-50 to-transparent',
    navActiveBorder: 'border-orange-600',
    navActiveText: 'text-orange-700',
    navHoverText: 'hover:text-orange-600',
    dropdownActiveBg: 'bg-orange-100',
    dropdownActiveText: 'text-orange-700',
    profileBg: 'from-orange-50 to-red-50',
  },
  rose: {
    name: 'rose',
    headerGradient: 'bg-gradient-to-r from-rose-600 to-pink-600',
    navActiveBg: 'bg-gradient-to-b from-rose-50 to-transparent',
    navActiveBorder: 'border-rose-600',
    navActiveText: 'text-rose-700',
    navHoverText: 'hover:text-rose-600',
    dropdownActiveBg: 'bg-rose-100',
    dropdownActiveText: 'text-rose-700',
    profileBg: 'from-rose-50 to-pink-50',
  },
}

interface ThemeContextType {
  theme: ThemeConfig
  themeType: ThemeType
  setTheme: (type: ThemeType) => void
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [themeType, setThemeType] = useState<ThemeType>('indigo')
  const [theme, setThemeObj] = useState<ThemeConfig>(themes['indigo'])

  useEffect(() => {
    const saved = localStorage.getItem('app-theme') as ThemeType | null
    if (saved && themes[saved]) {
      setThemeType(saved)
      setThemeObj(themes[saved])
    }
  }, [])

  const setTheme = (type: ThemeType) => {
    if (themes[type]) {
      setThemeType(type)
      setThemeObj(themes[type])
      localStorage.setItem('app-theme', type)
    }
  }

  return (
    <ThemeContext.Provider value={{ theme, themeType, setTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}

export function useTheme() {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider')
  }
  return context
}
