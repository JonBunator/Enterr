import { ReactNode } from "react";
import type { UserData } from '../../api/apiModels.ts'
import { CircularProgress, Typography } from "@mui/material";
import { useEffect, useState } from 'react'
import { Navigate } from 'react-router'
import { getUserData } from '../../api/apiRequests.ts'
import './ProtectedPage.scss'

interface ProtectedPageProps {
  loginPage?: boolean
  children?: ReactNode
}

export default function ProtectedPage(props: ProtectedPageProps) {
  const { loginPage, children } = props
  const [userData, setUserData] = useState<UserData | null>({ username: "debug", logged_in: true })
  const [loading, setLoading] = useState(false)


  useEffect(() => {
    console.log(userData)
  }, [userData]);

  if (loading) {
    return (
    <div className="loading-container">
      <CircularProgress size={64} />
      <Typography>Loading...</Typography>
    </div>
    )
  }

  if (!userData?.logged_in && !loginPage) {
    return <Navigate to="/login" replace />
  }
  else if (userData?.logged_in && loginPage) {
    return <Navigate to="/" replace />
  }

  return <>{children}</>
}
