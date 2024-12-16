import CssBaseline from '@mui/material/CssBaseline'
import { createTheme, ThemeProvider } from '@mui/material/styles'
import Content from './components/Content'
import WebSocketProvider from './components/WebSocketProvider'

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
  },
})
export default function App() {
  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <WebSocketProvider>
        <Content />
      </WebSocketProvider>
    </ThemeProvider>
  )
}
