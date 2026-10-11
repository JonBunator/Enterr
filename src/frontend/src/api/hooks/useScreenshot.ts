import { useQuery } from '@tanstack/react-query'

export function getScreenshotUrl(screenshotId: string): string {
  return `/api/screenshot/${screenshotId}`
}

async function loadImage(src: string): Promise<true> {
  return new Promise((resolve, reject) => {
    const image = new Image()
    image.onload = () => resolve(true)
    image.onerror = () => reject(new Error(`Could not load image ${src}`))
    image.src = src
  })
}

export interface ScreenshotAvailability {
  available: boolean
  pending: boolean
  failed: boolean
  refetch: () => void
}

/**
 * Checks if a screenshot can be loaded. A login can have a screenshot id without a
 * screenshot file, e.g. when it failed unexpectedly before the screenshot was taken.
 * The image is loaded through the browser, so it is cached for the following <img>.
 * Only a successful check is cached, a failed one is checked again on refetch.
 */
export function useScreenshotAvailable(screenshotId: string | null, enabled = true): ScreenshotAvailability {
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ['screenshotAvailable', screenshotId],
    queryFn: async () => loadImage(getScreenshotUrl(screenshotId!)),
    enabled: enabled && screenshotId !== null,
    staleTime: Infinity,
    retry: 1,
  })
  return {
    available: data === true,
    pending: isLoading,
    failed: isError,
    refetch: () => void refetch(),
  }
}
