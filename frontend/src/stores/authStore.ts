import { create } from 'zustand'
import { User } from '@/types'

interface AuthStore {
  user: User | null
  token: string | null
  isLoading: boolean
  isAuthenticated: boolean
  setUser: (user: User | null) => void
  setToken: (token: string | null) => void
  setLoading: (loading: boolean) => void
  logout: () => void
}

const AUTH_TOKEN_KEY = 'access_token'
const AUTH_USER_KEY = 'auth_user'

export const useAuthStore = create<AuthStore>((set) => ({
  user: JSON.parse(localStorage.getItem(AUTH_USER_KEY) || 'null'),
  token: localStorage.getItem(AUTH_TOKEN_KEY),
  isLoading: false,
  isAuthenticated: !!localStorage.getItem(AUTH_TOKEN_KEY),

  setUser: (user) => {
    if (user) {
      localStorage.setItem(AUTH_USER_KEY, JSON.stringify(user))
    } else {
      localStorage.removeItem(AUTH_USER_KEY)
    }
    set({ user })
  },

  setToken: (token) => {
    if (token) {
      localStorage.setItem(AUTH_TOKEN_KEY, token)
    } else {
      localStorage.removeItem(AUTH_TOKEN_KEY)
    }
    set({ token, isAuthenticated: !!token })
  },

  setLoading: (loading) => set({ isLoading: loading }),

  logout: () => {
    localStorage.removeItem(AUTH_TOKEN_KEY)
    localStorage.removeItem(AUTH_USER_KEY)
    set({ user: null, token: null, isAuthenticated: false })
  },
}))

export const getAuthToken = () => localStorage.getItem(AUTH_TOKEN_KEY)
export const removeAuthToken = () => {
  localStorage.removeItem(AUTH_TOKEN_KEY)
  localStorage.removeItem(AUTH_USER_KEY)
}
