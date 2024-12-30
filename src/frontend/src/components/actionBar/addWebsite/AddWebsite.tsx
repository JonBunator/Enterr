import type { ChangeWebsite } from '../../activity/activityRequests.ts'
import { PlusCircleIcon } from '@heroicons/react/24/outline'
import { Button } from '@mui/material'
import { useState } from 'react'
import { addWebsite } from '../../../api/apiRequests.ts'
import AddEditWebsite from '../../activity/AddEditWebsite.tsx'
import './AddWebsite.scss'

export default function AddWebsite() {
  const [open, setOpen] = useState(false)

  async function handleAdd(website: ChangeWebsite) {
    await addWebsite(website)
  }

  return (
    <>
      <Button className="add-website" variant="contained" onClick={() => setOpen(true)} startIcon={<PlusCircleIcon className="icon" />}>Add website</Button>
      <AddEditWebsite open={open} onClose={() => setOpen(false)} add onChange={value => void handleAdd(value)} />
    </>
  )
}
