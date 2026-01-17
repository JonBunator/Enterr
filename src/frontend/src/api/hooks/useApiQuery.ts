import { useMutation, useQueryClient, type UseMutationOptions } from '@tanstack/react-query'
import type { AxiosError } from 'axios'

// Generic mutation hook factory with automatic invalidation
interface UseApiMutationOptions<TData, TError, TVariables> extends Omit<UseMutationOptions<TData, TError, TVariables>, 'mutationFn'> {
  invalidateKeys?: (readonly unknown[])[] | ((data: TData, variables: TVariables) => (readonly unknown[])[])
}

export function useApiMutation<TData = unknown, TError = AxiosError, TVariables = void>(
  mutationFn: (variables: TVariables) => Promise<TData>,
  options?: UseApiMutationOptions<TData, TError, TVariables>
) {
  const queryClient = useQueryClient()

  return useMutation<TData, TError, TVariables>({
    mutationFn,
    onSuccess: (data, variables, onMutateResult, context) => {
      // Automatic cache invalidation
      if (options?.invalidateKeys) {
        const keysToInvalidate = typeof options.invalidateKeys === 'function'
          ? options.invalidateKeys(data, variables)
          : options.invalidateKeys

        keysToInvalidate.forEach(key => {
          queryClient.invalidateQueries({ queryKey: key })
        })
      }

      options?.onSuccess?.(data, variables, onMutateResult, context);
    },
    onError: options?.onError,
    onSettled: options?.onSettled,
    onMutate: options?.onMutate,
  })
}
