import { useQuery, useMutation, type UseQueryOptions } from '@tanstack/react-query'
import type { AxiosError } from 'axios'
import * as api from '../apiRequests'
import type { UserData } from '../apiModels'
import { queryClient } from '../queryClient'

// Query hooks
export function useUserData(
  options?: Omit<UseQueryOptions<UserData | null, AxiosError>, 'queryKey' | 'queryFn'>
) {
  return useQuery<UserData | null, AxiosError>({
    queryKey: ['user'],
    queryFn: api.getUserData,
    ...options,
  })
}

// Mutation hooks
export function useLoginUser() {
  return useMutation({
    mutationFn: ({ username, password }: { username: string; password: string }) =>
      api.loginUser(username, password),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['user'] })
    },
  })
}

export function useLogoutUser() {
  return useMutation({
    mutationFn: api.logoutUser,
    onSuccess: () => {
      queryClient.removeQueries();
    },
  })
}
