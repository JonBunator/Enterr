import type { ReactNode } from 'react'
import { createContext, forwardRef, useCallback, useContext, useImperativeHandle, useMemo, useState } from 'react'

interface Subscriber {
  identifier: string
  callback: () => boolean
}

interface FormContextType {
  subscribe: (subscriber: Subscriber) => void
  unsubscribe: (identifier: string) => void
}

const FormContext = createContext<FormContextType | undefined>(undefined)

export function useForm() {
  const context = useContext(FormContext)
  if (!context) {
    throw new Error('useForm must be used within a FormProvider')
  }
  return context
}
interface FormProviderProps {
  children: ReactNode
}

export interface FormProviderRef {
  /**
   * Validates all form elements and returns true when all fields are valid.
   */
  validate: () => boolean
  /**
   * Scrolls to first error element
   */
  scrollToError: () => void

}

export const FormProvider = forwardRef<FormProviderRef, FormProviderProps>((props, ref) => {
  const { children } = props
  const [subscribers, setSubscribers] = useState<Subscriber[]>([])

  const subscribe = useCallback((subscriber: Subscriber) => {
    setSubscribers(prevSubscribers => [...prevSubscribers, subscriber])
  }, [])

  const unsubscribe = useCallback((identifier: string) => {
    setSubscribers(prevSubscribers =>
      prevSubscribers.filter(subscriber => subscriber.identifier !== identifier),
    )
  }, [])

  const validate = () => {
    const results = subscribers.map(subscriber => subscriber.callback())
    return results.every(result => result)
  }

  const scrollToError = () => {
    const element = document.querySelector('.Mui-error')
    if (element !== null) {
      element.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  }

  useImperativeHandle(ref, () => ({
    validate,
    scrollToError,
  }))

  const value = useMemo(() => ({
    subscribe,
    unsubscribe,
  }), [subscribe, unsubscribe])

  return (
    <FormContext.Provider value={value}>
      {children}
    </FormContext.Provider>
  )
})
