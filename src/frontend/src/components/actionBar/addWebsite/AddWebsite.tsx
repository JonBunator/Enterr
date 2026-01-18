import type { ChangeWebsite } from '../../activity/model.ts'
import type { AddEditWebsiteRef } from '../../activity/AddEditWebsite.tsx'
import { PlusCircleIcon } from '@heroicons/react/24/outline'
import { Button } from '@mui/material'
import { useRef, useState } from 'react'
import { useAddWebsite } from '../../../api/hooks'
import AddEditWebsite from '../../activity/AddEditWebsite.tsx'
import { useSnackbar } from '../../provider/SnackbarProvider.tsx'
import './AddWebsite.scss'

export default function AddWebsite() {
  const [open, setOpen] = useState(false)

  const { success, error, loading } = useSnackbar()
  const ref = useRef<AddEditWebsiteRef | null>(null)
  const addMutation = useAddWebsite()

  async function handleAdd(website: ChangeWebsite) {
    setOpen(false)
    loading('Adding website...')
    try {
      await addMutation.mutateAsync(website)
      success('Website added successfully')
    }
    catch (e) {
      error('Failed to add website', (e as Error).message)
    }
    finally {
      ref.current?.resetForm()
    }
  }

  function handleClose() {
    setOpen(false)
    ref.current?.resetForm()
  }

  return (
    <>
      <Button className="add-website" variant="contained" onClick={() => setOpen(true)} startIcon={<PlusCircleIcon className="icon" />}>Add website</Button>
      <AddEditWebsite ref={ref} open={open} onClose={handleClose} add onChange={value => void handleAdd(value)} />
    </>
  )
}
