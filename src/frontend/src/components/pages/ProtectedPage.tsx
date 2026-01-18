import { ReactNode } from "react";
import { CircularProgress, Typography } from "@mui/material";
import { Navigate } from 'react-router'
import { useUserData } from "../../api/hooks"
import './ProtectedPage.scss'

interface ProtectedPageProps {
  loginPage?: boolean
  children?: ReactNode
}

export default function ProtectedPage(props: ProtectedPageProps) {
  const { loginPage, children } = props
  const { data: userData, isLoading, error } = useUserData()

  if (isLoading) {
    return (
    <div className="loading-container">
      <CircularProgress size={64} />
      <Typography>Loading...</Typography>
    </div>
    )
  }

  const isLoggedOut = !userData || error

  if (isLoggedOut && !loginPage) {
    return <Navigate to="/login" replace />
  }
  else if (!isLoggedOut && loginPage) {
    return <Navigate to="/" replace />
  }

  return <>{children}</>
}
