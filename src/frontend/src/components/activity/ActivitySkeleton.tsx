
import { Skeleton, TableCell, TableRow } from "@mui/material";
import "./ActivitySkeleton.scss";
import { AnimatePresence, motion } from "framer-motion";

export default function ActivitySkeleton() {

  return (
    <AnimatePresence>{
    Array.from({ length: 7 }).map((_, index) => (
      <TableRow component={motion.tr}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                layout
                className="activity-skeleton-table-row"
                key={index}>
        <TableCell>
          <div className="skeleton-status-container">
            <Skeleton variant="rounded" className="skeleton-status-icon" />
            <Skeleton variant="text" sx={{ fontSize: "1rem", width: 150 }} />
          </div>
        </TableCell>
        <TableCell>
          <Skeleton variant="text" sx={{ fontSize: "1rem", width: 150 }} />
        </TableCell>
        <TableCell>
          <Skeleton variant="text" sx={{ fontSize: "1rem", width: 100 }} />
        </TableCell>
        <TableCell>
          <Skeleton variant="text" sx={{ fontSize: "1rem", width: 100 }} />
        </TableCell>
        <TableCell>
          <div className="trigger">
            {Array.from({ length: Math.ceil(Math.random() * 3) }).map((_, i) => (
              <Skeleton key={i} variant="rounded" className="skeleton-status-icon" />
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
    </AnimatePresence>

  )
}
