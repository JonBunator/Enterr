import type { UseQueryOptions } from '@tanstack/react-query'
import type { AxiosError } from 'axios'
import type { UserData } from '../apiModels'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import * as api from '../apiRequests'

// Query hooks
export function useUserData(
  options?: Omit<UseQueryOptions<UserData | null, AxiosError>, 'queryKey' | 'queryFn'>,
) {
  return useQuery<UserData | null, AxiosError>({
    queryKey: ['user'],
    queryFn: api.getUserData,
    ...options,
  })
}

// Mutation hooks
export function useLoginUser() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ username, password }: { username: string, password: string }) =>
      api.loginUser(username, password),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['user'] })
    },
  })
}

export function useLogoutUser() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: api.logoutUser,
    onSuccess: () => {
      queryClient.removeQueries()
    },
  })
}
