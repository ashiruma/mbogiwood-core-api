// FILE: store/authStore.ts

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

type AuthState = {
    accessToken: string | null;
    refreshToken: string | null;
    isAuthenticated: boolean;
    login: (tokens: { access: string; refresh: string }) => void;
    logout: () => void;
};

export const useAuthStore = create<AuthState>()(
    persist(
        (set) => ({
            accessToken: null,
            refreshToken: null,
            isAuthenticated: false,
            login: (tokens) => set({
                accessToken: tokens.access,
                refreshToken: tokens.refresh,
                isAuthenticated: true,
            }),
            logout: () => set({
                accessToken: null,
                refreshToken: null,
                isAuthenticated: false,
            }),
        }),
        {
            name: 'auth-storage', // Name for the local storage item
        }
    )
);