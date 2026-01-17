import { Autocomplete, Button, Divider, Link, Typography } from "@mui/material";
import { ActionStatusCode, Notification } from "../../../api/apiModels.ts";
import './AddEditNotification.scss'
import { useEffect, useRef, useState } from "react";
import { ArrowTopRightOnSquareIcon } from "@heroicons/react/16/solid";
import ApprovalDialog from "../../ApprovalDialog.tsx";
import { useTestNotification } from "../../../api/hooks";
import { FormProvider, type FormProviderRef } from "../../form/FormProvider.tsx";
import TextFieldForm from "../../form/TextFieldForm.tsx";

interface AddEditNotificationProps {
  /**
   * When true, creation is displayed. Edit otherwise.
   */
  notification: Notification | null
  /**
   * Callback used when a new notification was created.
   * @param notification The created notification.
   */
  onCreate: (notification: Notification) => void
  /**
   * Callback used when a new notification was edited.
   * @param notification The edited notification.
   */
  onEdit: (notification: Notification) => void
  /**
   * Callback used when a new notification was deleted.
   * @param notification The deleted notification.
   */
  onDelete: (notification: Notification) => void
  /**
   * Callback invoked when action is canceled.
   */
  onCancel: () => void
}

const emptyNotification: Notification = {
  name: '',
  apprise_token: '',
  token: '',
  title: '',
  body: '',
  triggers: []
}

type TriggerOption = {
  label: string
  value: ActionStatusCode
}

const triggerOptions: TriggerOption[] = [
  {
    label: "Success",
    value: "SUCCESS"
  },
  {
    label: "Failure",
    value: "FAILED"
  },
  {
    label: "In Progress",
    value: "IN_PROGRESS"
  },
]

export default function AddEditNotification(props: AddEditNotificationProps) {
  const { notification, onCreate, onEdit, onDelete, onCancel } = props;
  const [currentNotification, setCurrentNotification] = useState<Notification>(notification ?? emptyNotification);
  const [deletionApprovalDialogOpen, setDeletionApprovalDialogOpen] = useState<boolean>(false)

  const formRef = useRef<FormProviderRef>(null)
  const testMutation = useTestNotification();

  useEffect(() => {
    setCurrentNotification(notification ?? emptyNotification);
  }, [notification]);


  /**
   * Returns true when the notification should be created. False when edited.
   */
  function isCreation(): boolean {
    return notification === null;
  }

  function handleTriggerChange(_: any, selectedOptions: TriggerOption[]) {
    setCurrentNotification((prev) => ({
      ...prev,
      triggers: selectedOptions.map(option => option.value)
    }));
  }

  async function editOrCreate() {
    if (formRef?.current) {
      const isValid = await formRef?.current.validate();
      if (isValid) {
        if (isCreation()) {
          onCreate(currentNotification);
        } else {
          onEdit(currentNotification);
        }
      }
      else {
        formRef?.current.scrollToError()
      }
    }
  }

  function deleteNotification() {
    if(notification?.id) {
      onDelete(notification);
    }
  }

  async function testCreate() {
    if (formRef?.current) {
      const isValid = await formRef?.current.validate();
      if (isValid) {
        await testMutation.mutateAsync(currentNotification);
      }
      else {
        formRef?.current.scrollToError()
      }
    }
  }

  function validateAppriseToken(value: string): string {
    if (value === '') {
      return 'Field is required';
    }
    const regex = /^\w*:\/\/.*$/
    if (value === undefined || !regex.test(value)) {
      return 'Invalid apprise token'
    }
    return ''
  }

  return (
    <FormProvider ref={formRef}>
      <div className="add-edit-notification">
        <ApprovalDialog
          open={deletionApprovalDialogOpen}
          onClose={() => setDeletionApprovalDialogOpen(false)}
          onApproval={deleteNotification}
          header="Delete notification"
          description="Are you sure you want to delete this notification?"
          approvalText="Delete"
        />
        <div>
          <Typography variant="h6">{isCreation() ? 'Add' : 'Edit'} Notification</Typography>
          <Typography sx={{ color: 'text.secondary', fontSize: 14 }}>
            {isCreation() ? 'Configure a new notification' : 'Edit an existing notification'}
          </Typography>
        </div>
        <div className="section">
          <TextFieldForm
            identifier="name"
            placeholder="My notification"
            variant="filled"
            helperText="Name is used to identify the notification"
            label="Name"
            required
            fullWidth
            name="name"
            value={currentNotification.name}
            onChange={(event) => setCurrentNotification((prev) => ({
              ...prev,
              name: event.target.value,
            }))}
          />

          <Autocomplete
            multiple
            options={triggerOptions}
            getOptionLabel={(option) => option.label}
            value={triggerOptions.filter(opt => currentNotification.triggers.includes(opt.value))}
            onChange={handleTriggerChange}
            renderInput={(params) => (
              <TextFieldForm
                identifier="triggers"
                className={`${currentNotification.triggers.length !== 0 ? "value-selected" : "no-value-selected"}`}
                {...params}
                required
                variant="filled"
                label="Triggers"
                validationValue={currentNotification.triggers.join(";")}
                helperText="Defines when a notification should be triggered"
              />
            )}
          />
        </div>

        <Divider />

        <div className="section">
          <Typography sx={{ color: 'text.secondary', fontSize: 14 }}>
            Enterr uses <Link rel="noopener" href="https://github.com/caronc/apprise" target="_blank">
            Apprise <ArrowTopRightOnSquareIcon className="icon-small" />
          </Link> for notifications
          </Typography>

          <TextFieldForm
            identifier="token"
            placeholder="discord://webhook_id/webhook_token"
            label="Apprise Token"
            variant="filled"
            required
            fullWidth
            onValidate={validateAppriseToken}
            name="apprise_token"
            value={currentNotification.apprise_token}
            onChange={(event) => setCurrentNotification((prev) => ({
              ...prev,
              apprise_token: event.target.value,
            }))}
          />

          <TextFieldForm
            identifier="title"
            label="Title"
            variant="filled"
            required
            fullWidth
            name="title"
            value={currentNotification.title}
            onChange={(event) => setCurrentNotification((prev) => ({
              ...prev,
              title: event.target.value
            }))}
            helperText="Title is used as the subject of the notification"
          />

          <TextFieldForm
            identifier="body"
            variant="filled"
            label="Body"
            required
            fullWidth
            multiline
            rows={10}
            name="body"
            value={currentNotification.body}
            onChange={(event) => setCurrentNotification((prev) => ({
              ...prev,
              body: event.target.value
            }))}
            helperText={<>Body is used as the content of the notification. It can contain variables (See <Link rel="noopener" href="https://github.com/JonBunator/Enterr/wiki" target="_blank">Docs <ArrowTopRightOnSquareIcon className="icon-small" /></Link> for more information).</>}
          />
        </div>

        <div className="button-container">
          <div className="button-group">
            {!isCreation() && <Button variant="contained" color="error" className="test-notification" onClick={() => setDeletionApprovalDialogOpen(true)}>Delete</Button>}
            <Button variant="outlined" onClick={testCreate}>Test notification</Button>
          </div>
          <div className="button-group">
            <Button onClick={onCancel}>Cancel</Button>
            <Button onClick={editOrCreate} variant="contained">{isCreation() ? "Create" : "Save"}</Button>
          </div>
        </div>
      </div>
    </FormProvider>
  );
}