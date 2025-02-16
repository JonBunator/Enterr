import type { SlideProps } from '@mui/material'
import { Alert, AlertTitle, CircularProgress, Slide, Snackbar } from '@mui/material'
import React, { createContext, useCallback, useContext, useMemo, useState } from 'react'

interface SnackbarContextType {
  success: (title: string, message?: string) => void
  error: (title: string, message?: string) => void
  loading: (title: string, message?: string) => void
  clear: () => void
}

const SnackbarContext = createContext<SnackbarContextType | undefined>(undefined)

interface SnackbarProviderProps {
  children: React.ReactNode
}

function SlideTransition(props: SlideProps) {
  return <Slide {...props} direction="up" />
}
export default function SnackbarProvider({ children }: SnackbarProviderProps) {
  const [snackbar, setSnackbar] = useState<{ title: string, message: string, severity: 'success' | 'error' | 'info', open: boolean }>({
    title: '',
    message: '',
    severity: 'success',
    open: false,
  })

  const handleClose = useCallback(() => {
    setSnackbar(prev => ({ ...prev, open: false }))
  }, [])

  const success = useCallback((title: string, message?: string) => {
    setSnackbar({ title, message: message ?? '', severity: 'success', open: true })
  }, [])

  const error = useCallback((title: string, message?: string) => {
    setSnackbar({ title, message: message ?? '', severity: 'error', open: true })
  }, [])

  const loading = useCallback((title: string, message?: string) => {
    setSnackbar({ title, message: message ?? '', severity: 'info', open: true })
  }, [])

  const clear = useCallback(() => {
    setSnackbar(prev => ({ ...prev, open: false }))
  }, [])

  const value = useMemo(
    () => ({
      success,
      error,
      loading,
      clear,
    }),
    [success, error, loading, clear],
  )

  return (
    <SnackbarContext value={value}>
      {children}
      <Snackbar open={snackbar.open} autoHideDuration={5000} TransitionComponent={SlideTransition} onClose={handleClose} anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}>
        <Alert onClose={handleClose} severity={snackbar.severity} variant="filled" sx={{ width: '400px' }} icon={snackbar.severity === 'info' ? <CircularProgress size={18} color="inherit" /> : undefined}>
          {snackbar.message !== '' && <AlertTitle>{snackbar.title}</AlertTitle>}
          {snackbar.message === '' ? snackbar.title : snackbar.message}
        </Alert>
      </Snackbar>
    </SnackbarContext>
  )
}

export function useSnackbar(): SnackbarContextType {
  const context = useContext(SnackbarContext)
  if (!context) {
    throw new Error('useSnackbar must be used within a SnackbarProvider')
  }
  return context
}
