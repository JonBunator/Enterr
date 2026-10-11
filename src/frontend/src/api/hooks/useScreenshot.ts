import { useQuery } from '@tanstack/react-query'

export function getScreenshotUrl(screenshotId: string): string {
  return `/api/screenshot/${screenshotId}`
}

async function canLoadImage(src: string): Promise<boolean> {
  return new Promise((resolve) => {
    const image = new Image()
    image.onload = () => resolve(true)
    image.onerror = () => resolve(false)
    image.src = src
  })
}

/**
 * Checks if a screenshot can be loaded. A login can have a screenshot id without a
 * screenshot file, e.g. when it failed unexpectedly before the screenshot was taken.
 * The image is loaded through the browser, so it is cached for the following <img>.
 */
export function useScreenshotAvailable(screenshotId: string | null, enabled = true): boolean {
  const { data } = useQuery({
    queryKey: ['screenshotAvailable', screenshotId],
    queryFn: async () => canLoadImage(getScreenshotUrl(screenshotId!)),
    enabled: enabled && screenshotId !== null,
    staleTime: Infinity,
  })
  return data === true
}
