import {
  Button,
  Drawer, Skeleton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography
} from "@mui/material";
import "./NotificationsSettings.scss";
import { EditNotification, Notification } from "../../../api/apiModels.ts";
import { PlusCircleIcon } from "@heroicons/react/24/outline";
import { useState } from "react";
import Triggers from "./Triggers.tsx";
import {
  useNotifications,
  useAddNotification,
  useEditNotification,
  useDeleteNotification
} from "../../../api/hooks";
import AddEditNotification from "./AddEditNotification.tsx";
import { useSnackbar } from "../../provider/SnackbarProvider.tsx";
import EmptyState from "../../activity/EmptyState.tsx";

export default function NotificationsSettings() {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [editCreateNotification, setEditCreateNotification] = useState<Notification | null>(null);
  const { error, success, loading } = useSnackbar();
  
  const { data: notifications = [], isLoading } = useNotifications();
  const addMutation = useAddNotification();
  const editMutation = useEditNotification();
  const deleteMutation = useDeleteNotification();


  function openEditNotificationDrawer(notification: Notification) {
    setEditCreateNotification(notification);
    setDrawerOpen(true);
  }

  function openCreateNotificationDrawer() {
    setEditCreateNotification(null);
    setDrawerOpen(true);
  }

  async function create(notification: Notification) {
    setDrawerOpen(false);
    loading('Adding notification...')
    try {
      await addMutation.mutateAsync(notification);
      success('Notification added successfully');
    } catch (e) {
      error("Failed to add notification", (e as Error).message);
    }
  }

  async function edit(notification: Notification) {
    setDrawerOpen(false);
    loading('Editing notification...')
    try {
      await editMutation.mutateAsync(notification as EditNotification);
      success('Notification edited successfully');
    } catch (e) {
      error("Failed to edit notification", (e as Error).message);
    }
  }

  async function remove(notification: Notification) {
    setDrawerOpen(false);
    loading('Deleting notification...')
    try {
      await deleteMutation.mutateAsync(notification.id!);
      success('Notification deleted successfully');
    } catch (e) {
      error("Failed to delete notification", (e as Error).message);
    }
  }

  function getType(token: string) {
    const type = token.split("://")[0];
    if (!type) {
      return "Unknown";
    }
    return type.charAt(0).toUpperCase() + type.slice(1);
  }

  return (
    <div className="notifications-settings">
      <div>
        <Typography typography="h6">Notifications</Typography>
        <Typography sx={{ color: "text.secondary", fontSize: 14 }}>
          Configure notifications for login updates
        </Typography>
      </div>
      <TableContainer className="notifications-table">
        <Table stickyHeader>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Triggers</TableCell>
              <TableCell align="right">
                <Button
                  onClick={() => openCreateNotificationDrawer()}
                  startIcon={<PlusCircleIcon className="icon" />}
                  variant="outlined"
                >
                  Add Notification
                </Button>
              </TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {isLoading &&
              Array.from({ length: 5 }).map((_, index) => (
                <TableRow className="table-row" key={index}>
                  <TableCell>
                    <Skeleton variant="text" sx={{ fontSize: "1rem" }} />
                  </TableCell>
                  <TableCell>
                    <Skeleton variant="text" sx={{ fontSize: "1rem" }} />
                  </TableCell>
                  <TableCell>
                    <div className="trigger">
                      {Array.from({ length: Math.ceil(Math.random() * 2) }).map((_, i) => (
                        <Skeleton key={i} variant="rounded" className="skeleton-chip" />
                      ))}
                    </div>
                  </TableCell>
                  <TableCell align="right">
                    <Skeleton
                      variant="text"
                      className="skeleton-edit"
                    />
                  </TableCell>
                </TableRow>
              ))}
            {notifications.length === 0 && !isLoading ? (
              <TableRow className="table-row">
                <TableCell colSpan={4}>
                  <EmptyState
                    noData
                    noDataHelperText="Add a notification to get started"
                  />
                </TableCell>
              </TableRow>
            ) : (
              notifications.map((notificaton, index) => (
                <TableRow key={index} className="table-row">
                  <TableCell>{notificaton.name}</TableCell>
                  <TableCell>{getType(notificaton.apprise_token)}</TableCell>
                  <TableCell>
                    <Triggers triggers={notificaton.triggers} />
                  </TableCell>
                  <TableCell align="right">
                    <Button
                      onClick={() => openEditNotificationDrawer(notificaton)}
                    >
                      Edit
                    </Button>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
      <Drawer
        anchor="right"
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
      >
        <AddEditNotification
          onDelete={remove}
          onCreate={create}
          onEdit={edit}
          onCancel={() => setDrawerOpen(false)}
          notification={editCreateNotification}
        />
      </Drawer>
    </div>
  );
}