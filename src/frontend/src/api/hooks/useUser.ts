import { useQuery, useMutation, useQueryClient, type UseQueryOptions } from '@tanstack/react-query'
import type { AxiosError } from 'axios'
import * as api from '../apiRequests'
import type { UserData } from '../apiModels'

// Query hooks
export function useUserData(
  options?: Omit<UseQueryOptions<UserData, AxiosError>, 'queryKey' | 'queryFn'>
) {
  return useQuery<UserData, AxiosError>({
    queryKey: ['user', 'data'],
    queryFn: api.getUserData,
    ...options,
  })
}

// Mutation hooks
export function useLoginUser() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ username, password }: { username: string; password: string }) =>
      api.loginUser(username, password),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user'] }).then();
    },
  })
}

export function useLogoutUser() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: api.logoutUser,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["user"] }).then();
    },
  })
}
