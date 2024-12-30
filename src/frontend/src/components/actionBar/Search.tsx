import { MagnifyingGlassIcon } from '@heroicons/react/24/outline'
import { Autocomplete, InputAdornment, TextField } from '@mui/material'
import './Search.scss'

export default function Search() {
  return (
    <Autocomplete
      className="search"
      disablePortal
      options={[]}
      renderInput={params => (
        <TextField
          {...params}
          placeholder="Search..."
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
