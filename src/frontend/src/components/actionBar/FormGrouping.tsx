import type { ReactNode } from 'react'
import { Checkbox, FormControlLabel, Paper, Typography } from '@mui/material'
import { motion } from 'framer-motion'
import useMeasure from 'react-use-measure'
import './FormGrouping.scss'

interface FormGroupingProps {
  title: ReactNode
  subtitle?: ReactNode
  elevation?: number
  column?: boolean
  backgroundElevation?: number
  disableCheckbox?: boolean
  checked?: boolean
  onChange?: (checked: boolean) => void
  children?: ReactNode
}

interface ResizablePanelProps {
  keyProp?: string | number
  children?: ReactNode
}

function ResizablePanel(props: ResizablePanelProps) {
  const [ref, { height }] = useMeasure()
  const { keyProp, children } = props
  return (
    <motion.div animate={{ height }} transition={{ duration: 0.3 }}>
      <motion.div key={keyProp} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.8 }}>
        <div ref={ref}>
          {children}
        </div>
      </motion.div>
    </motion.div>
  )
}

export default function FormGrouping(props: FormGroupingProps) {
  const { title, subtitle, elevation, column, backgroundElevation, disableCheckbox, checked, onChange, children } = props
  return (
    <Paper className="form-grouping" elevation={elevation ?? 12}>
      {disableCheckbox
        ? (
            <Typography className="form-grouping-title">
              <Paper
                elevation={backgroundElevation ?? 24}
                className="form-grouping-title-before"
              />
              {title}
            </Typography>
          )
        : (
            <div className="form-grouping-checkbox">
              <Paper
                elevation={backgroundElevation ?? 24}
                className="form-grouping-checkbox-before"
              />
              <FormControlLabel
                className="form-grouping-checkbox-label"
                control={(
                  <Checkbox
                    checked={checked}
                    onChange={event => onChange?.(event.target.checked)}
                  />
                )}
                label={title}
              />
            </div>
          )}
      <ResizablePanel keyProp={checked === true ? 1 : 0}>
        {(checked || checked === undefined) && (
          <div className={`form-grouping-container ${column === true ? 'column' : 'row'}`}>
            {children}
          </div>
        )}
      </ResizablePanel>
      {subtitle !== undefined && (
        <Typography
          className="form-grouping-subtitle"
          sx={{ color: 'text.secondary' }}
        >
          {subtitle}
        </Typography>
      )}
    </Paper>
  )
}
