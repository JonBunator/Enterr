import type { ReactNode } from 'react'
import type { UserData } from '../../api/apiModels.ts'
import { CircularProgress } from '@mui/material'
import { useEffect, useState } from 'react'
import { Navigate } from 'react-router'
import { getUserData } from '../../api/apiRequests.ts'

interface ProtectedPageProps {
  loginPage?: boolean
  children?: ReactNode
}

export default function ProtectedPage(props: ProtectedPageProps) {
  const { loginPage, children } = props
  const [userData, setUserData] = useState<UserData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getUserData()
      .then(data => setUserData(data))
      .catch(error => console.error(error))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return <CircularProgress size={64} />
  }

  if (!userData?.logged_in && !loginPage) {
    return <Navigate to="/login" replace />
  }
  else if (userData?.logged_in && loginPage) {
    return <Navigate to="/" replace />
  }

  return <>{children}</>
}
