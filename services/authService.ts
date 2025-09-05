// FILE: services/authService.ts

import apiClient from "@/lib/api";
import { AuthData, AuthResponse } from "@/types";

export const registerUser = async (userData: AuthData): Promise<AuthResponse> => {
    // This must be a POST request to create a new user.
    const response = await apiClient.post<AuthResponse>('/api/users/', userData);
    return response.data;
};

export const loginUser = async (userData: AuthData): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>('/api/jwt/create/', userData);
    return response.data;
};