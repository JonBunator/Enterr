import { MagnifyingGlassIcon } from '@heroicons/react/24/outline'
import { Autocomplete, InputAdornment, TextField } from '@mui/material'
import { useEffect, useState } from 'react'
import './Search.scss'

interface SearchProps {
  value?: string
  onChange?: (value: string) => void
}

export default function Search(props: SearchProps) {
  const { value, onChange } = props
  const [inputValue, setInputValue] = useState<string | undefined>(value)
  const [timer, setTimer] = useState<NodeJS.Timeout | null>(null)

  useEffect(() => {
    if (value !== inputValue) {
      setInputValue(value)
    }
  }, [value])

  return (
    <Autocomplete
      className="search"
      disablePortal
      freeSolo
      options={[]}
      inputValue={inputValue ?? ''}
      onInputChange={(_event, newValue, reason) => {
        if (reason === 'reset') return
        setInputValue(newValue)

        if (timer) {
          clearTimeout(timer)
        }

        const newTimer = setTimeout(() => {
          onChange?.(newValue)
        }, 200)

        setTimer(newTimer)
      }}
      renderInput={params => (
        <TextField
          {...params}
          placeholder="Search..."
          slotProps={{
            input: {
              ...params.InputProps,
              startAdornment: (
                <InputAdornment position="start">
                  <MagnifyingGlassIcon className="icon" />
                </InputAdornment>
              ),
            },
          }}
        />
      )}
    />
  )
}
