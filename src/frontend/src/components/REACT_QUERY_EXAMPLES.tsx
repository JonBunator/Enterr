/**
 * EXAMPLE: How to use React Query hooks in your components
 * 
 * This file demonstrates best practices for using the new React Query hooks
 * throughout your application. Copy these patterns into your actual components.
 */

import { useWebsites, useAddWebsite, useEditWebsite, useDeleteWebsite } from '../api/hooks'
import type { Website } from '../api/apiModels'
import type { ChangeWebsite } from './activity/activityRequests'

// ============================================================================
// Example 1: Fetching data with loading and error states
// ============================================================================

export function WebsiteListExample() {
  const { data: websites, isLoading, error, refetch } = useWebsites()

  if (isLoading) {
    return <div>Loading websites...</div>
  }

  if (error) {
    return (
      <div>
        <p>Error loading websites: {error.message}</p>
        <button onClick={() => refetch()}>Retry</button>
      </div>
    )
  }

  return (
    <div>
      <h2>Websites ({websites?.length || 0})</h2>
      {websites?.map((website) => (
        <WebsiteCard key={website.id} website={website} />
      ))}
    </div>
  )
}

// ============================================================================
// Example 2: Adding a new item with mutation
// ============================================================================

export function AddWebsiteExample() {
  const addWebsite = useAddWebsite()

  const handleSubmit = (formData: ChangeWebsite) => {
    addWebsite.mutate(formData, {
      onSuccess: () => {
        console.log('Website added successfully!')
        // The websites list is automatically refetched
      },
      onError: (error) => {
        console.error('Failed to add website:', error.message)
      }
    })
  }

  return (
    <form onSubmit={(e) => {
      e.preventDefault()
      const formData = {} // Get form data
      handleSubmit(formData as ChangeWebsite)
    }}>
      {/* Form fields */}
      
      <button type="submit" disabled={addWebsite.isPending}>
        {addWebsite.isPending ? 'Adding...' : 'Add Website'}
      </button>
      
      {addWebsite.isError && (
        <div className="error">{addWebsite.error.message}</div>
      )}
      
      {addWebsite.isSuccess && (
        <div className="success">Website added successfully!</div>
      )}
    </form>
  )
}

// ============================================================================
// Example 3: Editing an item
// ============================================================================

function WebsiteCard({ website }: { website: Website }) {
  const editWebsite = useEditWebsite()
  const deleteWebsite = useDeleteWebsite()

  const handleTogglePause = () => {
    editWebsite.mutate({
      id: website.id,
      website: { paused: !website.paused }
    })
  }

  const handleDelete = () => {
    if (confirm('Are you sure you want to delete this website?')) {
      deleteWebsite.mutate(website.id, {
        onSuccess: () => {
          console.log('Website deleted!')
          // List automatically refetches
        }
      })
    }
  }

  return (
    <div>
      <h3>{website.name}</h3>
      <p>{website.url}</p>
      <p>Status: {website.paused ? 'Paused' : 'Active'}</p>
      
      <button 
        onClick={handleTogglePause}
        disabled={editWebsite.isPending}
      >
        {editWebsite.isPending ? 'Updating...' : website.paused ? 'Resume' : 'Pause'}
      </button>
      
      <button 
        onClick={handleDelete}
        disabled={deleteWebsite.isPending}
      >
        {deleteWebsite.isPending ? 'Deleting...' : 'Delete'}
      </button>
    </div>
  )
}

// ============================================================================
// Example 4: Using optimistic updates for instant UI feedback
// ============================================================================

import { useQueryClient } from '@tanstack/react-query'

export function OptimisticUpdateExample({ website }: { website: Website }) {
  const queryClient = useQueryClient()
  const editWebsite = useEditWebsite()

  const handleTogglePause = () => {
    const newPausedState = !website.paused

    editWebsite.mutate(
      {
        id: website.id,
        website: { paused: newPausedState }
      },
      {
        // Optimistically update the UI before the request completes
        onMutate: async (variables) => {
          // Cancel outgoing refetches
          await queryClient.cancelQueries({ queryKey: ['websites', 'detail', website.id] })

          // Snapshot the previous value
          const previousWebsite = queryClient.getQueryData(['websites', 'detail', website.id])

          // Optimistically update to the new value
          queryClient.setQueryData(['websites', 'detail', website.id], (old: Website | undefined) => {
            if (!old) return old
            return { ...old, paused: newPausedState }
          })

          // Return context with the previous value
          return { previousWebsite }
        },
        
        // If the mutation fails, use the context to roll back
        onError: (err, variables, context) => {
          if (context?.previousWebsite) {
            queryClient.setQueryData(
              ['websites', 'detail', website.id],
              context.previousWebsite
            )
          }
        },
        
        // Always refetch after error or success
        onSettled: () => {
          queryClient.invalidateQueries({ queryKey: ['websites', 'detail', website.id] })
        }
      }
    )
  }

  return (
    <button onClick={handleTogglePause}>
      {website.paused ? 'Resume' : 'Pause'}
    </button>
  )
}

// ============================================================================
// Example 5: Using dependent queries
// ============================================================================

import { useWebsite, useLoginHistory } from '../api/hooks'

export function WebsiteDetailsWithHistory({ websiteId }: { websiteId: number }) {
  // First query: Get website details
  const { 
    data: website, 
    isLoading: isLoadingWebsite 
  } = useWebsite(websiteId)

  // Second query: Only runs if websiteId > 0 (enabled by default in the hook)
  const { 
    data: history, 
    isLoading: isLoadingHistory 
  } = useLoginHistory(websiteId)

  if (isLoadingWebsite) {
    return <div>Loading website...</div>
  }

  if (!website) {
    return <div>Website not found</div>
  }

  return (
    <div>
      <h2>{website.name}</h2>
      <p>{website.url}</p>
      
      <h3>Login History</h3>
      {isLoadingHistory ? (
        <div>Loading history...</div>
      ) : (
        <ul>
          {history?.map((entry) => (
            <li key={entry.id}>
              {entry.execution_started} - {entry.execution_status}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

// ============================================================================
// Example 6: Background refetching
// ============================================================================

export function AutoRefreshingList() {
  const { data: websites } = useWebsites({
    refetchInterval: 30000, // Refetch every 30 seconds
    refetchIntervalInBackground: false, // Don't refetch when tab is not visible
  })

  return (
    <div>
      {websites?.map((website) => (
        <div key={website.id}>{website.name}</div>
      ))}
    </div>
  )
}

// ============================================================================
// Example 7: Conditional queries
// ============================================================================

export function ConditionalQueryExample({ shouldFetch }: { shouldFetch: boolean }) {
  const { data: websites } = useWebsites({
    enabled: shouldFetch, // Only run the query if shouldFetch is true
  })

  if (!shouldFetch) {
    return <div>Query is disabled</div>
  }

  return <div>{websites?.length || 0} websites</div>
}

// ============================================================================
// Example 8: Handling mutation side effects
// ============================================================================

import { useNavigate } from 'react-router'

export function AddWebsiteWithNavigation() {
  const navigate = useNavigate()
  const addWebsite = useAddWebsite()

  const handleSubmit = (formData: ChangeWebsite) => {
    addWebsite.mutate(formData, {
      onSuccess: () => {
        // Navigate to home page after successful addition
        navigate('/')
      }
    })
  }

  return (
    <div>
      {/* Form implementation */}
    </div>
  )
}

// ============================================================================
// Example 9: Using pagination (infinite scroll)
// ============================================================================

import { useLoginHistoryPaginated } from '../api/hooks'

export function InfiniteScrollHistory({ websiteId }: { websiteId: number }) {
  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading,
  } = useLoginHistoryPaginated(websiteId, 10)

  if (isLoading) {
    return <div>Loading...</div>
  }

  return (
    <div>
      <h3>Login History</h3>
      {data?.pages.map((page, pageIndex) => (
        <div key={pageIndex}>
          {page.items.map((history) => (
            <div key={history.id}>
              {history.execution_started} - {history.execution_status}
            </div>
          ))}
        </div>
      ))}

      {hasNextPage && (
        <button
          onClick={() => fetchNextPage()}
          disabled={isFetchingNextPage}
        >
          {isFetchingNextPage ? 'Loading more...' : 'Load More'}
        </button>
      )}

      {!hasNextPage && data?.pages.length > 0 && (
        <p>No more results</p>
      )}
    </div>
  )
}

// ============================================================================
// Example 10: Manual cache manipulation
// ============================================================================

export function ManualCacheExample() {
  const queryClient = useQueryClient()

  const handleRefreshAll = () => {
    // Invalidate all website queries
    queryClient.invalidateQueries({ queryKey: ['websites'] })
  }

  const handleClearCache = () => {
    // Remove all cached data
    queryClient.clear()
  }

  const handleSetCacheData = () => {
    // Manually set cache data (useful for optimistic updates)
    queryClient.setQueryData(['websites', 'list'], [
      { id: 1, name: 'Example', url: 'https://example.com' } as Website
    ])
  }

  return (
    <div>
      <button onClick={handleRefreshAll}>Refresh All Websites</button>
      <button onClick={handleClearCache}>Clear All Cache</button>
      <button onClick={handleSetCacheData}>Set Example Data</button>
    </div>
  )
}
