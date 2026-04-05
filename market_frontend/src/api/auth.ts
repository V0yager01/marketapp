import client from './client'

export interface AuthResponse {
  access_token: string
  token_type: string
}

export interface RegisterPayload {
  email: string
  password: string
}

export interface LoginPayload {
  email: string
  password: string
}

export const register = (data: RegisterPayload) =>
  client.post<AuthResponse>('/auth/register', data).then((r) => r.data)

export const login = (data: LoginPayload) =>
  client.post<AuthResponse>('/auth/login', data).then((r) => r.data)
