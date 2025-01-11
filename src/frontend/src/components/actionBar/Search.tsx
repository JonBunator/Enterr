import { MagnifyingGlassIcon } from '@heroicons/react/24/outline'
import { Autocomplete, InputAdornment, TextField } from '@mui/material'
import './Search.scss'

interface SearchProps {
  value?: string
  onChange?: (value: string) => void
}

export default function Search(props: SearchProps) {
  const { value, onChange } = props
  return (
    <Autocomplete
      className="search"
      disablePortal
      options={[]}
      renderInput={params => (
        <TextField
          {...params}
          placeholder="Search..."
          value={value}
          onChange={event => onChange?.(event.target.value)}
          slotProps={{
            input: {
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
