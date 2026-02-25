import React, { useEffect, useState } from "react";
import {
  Box,
  CircularProgress,
  Stack,
  Avatar,
  Typography,
} from "@mui/material";
import botIcon from "../../assets/icons/botIcon.svg";
import styles from "./SCNInternalReviewAuditTab.module.scss";
import { fetchScnQmsAudit } from "src/services/scn";
import { ScnAuditItem } from "src/types";

// --- Types ---
interface User {
  name: string;
  email: string;
  avatar?: string;
}

interface TimelineEvent {
  id: number;
  type: "approved" | "rejected" | "review" | "edited" | "created";
  timestamp: string;
  title: string;
  description: string;
  user?: User;
}

// --- Helpers ---

/**
 * Formats an ISO date string to a human-readable label.
 * e.g. "2026-02-25T14:20:00Z" → "Feb 25, 2026"
 */
function formatDate(iso: string): string {
  try {
    return new Date(iso).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  } catch {
    return iso;
  }
}

function humanizeField(field: string): string {
  return field.replace(/_/g, " ");
}

function deriveType(item: ScnAuditItem): TimelineEvent["type"] {
  const field = item.changed_field?.toLowerCase() ?? "";
  const newVal = (item.new_value ?? "").toLowerCase();

  if (newVal === "approved") return "approved";
  if (newVal === "rejected") return "rejected";
  if (field === "classification" && item.old_value === null) return "created";
  if (field.includes("review")) return "review";
  return "edited";
}

function buildDescription(item: ScnAuditItem): string {
  const date = formatDate(item.created_at);
  const field = humanizeField(item.changed_field);
  const by = item.changed_by ?? "System";

  if (item.old_value === null) {
    return `${by} initiated the ${field} for ${item.scn_id} on ${date}.`;
  }
  return `${by} changed the ${field} from ${item.old_value} to ${item.new_value ?? "—"} on ${date}.`;
}

function mapAuditItemToEvent(item: ScnAuditItem): TimelineEvent {
  const type = deriveType(item);
  const date = formatDate(item.created_at);
  const field = humanizeField(item.changed_field);

  const isUserAction = type === "edited" || type === "created";

  return {
    id: item.id,
    type,
    timestamp: date.toUpperCase(),
    title: `${item.scn_id} – ${field}`,
    description: buildDescription(item),
    // Show user avatar card for edit/create events where we have an email
    user: isUserAction
      ? {
          name: item.changed_by,
          email: item.changed_by,
        }
      : undefined,
  };
}

// --- Sub-Components (preserved exactly) ---

const TimelineItem = ({
  item,
  isLast,
}: {
  item: TimelineEvent;
  isLast: boolean;
}) => {
  const { type, timestamp, title, description, user } = item;

  const renderContentHeader = () => {
    if (user) {
      return (
        <React.Fragment>
          <Box className={styles.headerRow}>
            <Avatar
              src={user.avatar}
              alt={user.name}
              className={styles.userAvatar}
            />
            <Box className={styles.titleContainer}>
              <Typography
                component="div"
                className={styles.title}
                style={{ fontSize: "14px" }}
              >
                <span className={styles.userName}>{user.name}</span>
                <span className={styles.actionText}>
                  {type === "created" ? "Created" : "has edited the file"}
                </span>
                <span className={styles.recordName}>
                  {type === "created" ? title : `${title}`}
                </span>
              </Typography>
              <span className={styles.userEmail}>{user.email}</span>
            </Box>
          </Box>
        </React.Fragment>
      );
    } else {
      // System/Status Layout
      return (
        <Box className={styles.headerRow}>
          <img src={botIcon} alt="Bot Icon" className={styles.botAvatar} />
          <Typography className={styles.title}>{title}</Typography>
        </Box>
      );
    }
  };

  return (
    <Box className={styles.timelineItem}>
      {/* Left Indicator Column */}
      <Box className={styles.timelineLeft}>
        <Box className={`${styles.timelineDot} ${styles[type]}`} />
        {!isLast && (
          <Box className={`${styles.timelineLine} ${styles[type]}`} />
        )}
      </Box>

      {/* Right Content Column */}
      <Stack className={styles.timelineContent}>
        <Typography className={styles.timestamp}>{timestamp}</Typography>
        {renderContentHeader()}
        <Typography className={styles.description}>{description}</Typography>
      </Stack>
    </Box>
  );
};

const ActivityTimeline = ({ data }: { data: TimelineEvent[] }) => {
  return (
    <Box className={styles.timelineContainer}>
      {data.map((item, index) => (
        <TimelineItem
          key={item.id}
          item={item}
          isLast={index === data.length - 1}
        />
      ))}
    </Box>
  );
};

// --- Main Component ---

interface SCNInternalReviewAuditTabProps {
  /** SCN reference number, e.g. "SCN-1234" */
  scnId?: string | null;
}

const SCNInternalReviewAuditTab: React.FC<SCNInternalReviewAuditTabProps> = ({
  scnId,
}) => {
  const [events, setEvents] = useState<TimelineEvent[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!scnId) {
      setEvents([]);
      return;
    }

    let cancelled = false;

    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await fetchScnQmsAudit(scnId);
        if (cancelled) return;

        if (res?.success && res.data?.items?.length > 0) {
          setEvents(res.data.items.map(mapAuditItemToEvent));
        } else {
          setEvents([]);
        }
      } catch (err: any) {
        if (!cancelled) {
          setError(err?.message ?? "Failed to load audit history.");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    load();

    return () => {
      cancelled = true;
    };
  }, [scnId]);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" py={6}>
        <CircularProgress size={28} sx={{ color: "#437ef7" }} />
      </Box>
    );
  }

  if (error) {
    return (
      <Box py={6} textAlign="center">
        <Typography sx={{ color: "#d32f2f", fontSize: 14 }}>{error}</Typography>
      </Box>
    );
  }

  if (!scnId || events.length === 0) {
    return (
      <Box py={6} textAlign="center">
        <Typography sx={{ color: "#6b7280", fontSize: 14 }}>
          {scnId
            ? `No audit history is available for ${scnId}.`
            : "No SCN selected."}
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      <ActivityTimeline data={events} />
    </Box>
  );
};

export default SCNInternalReviewAuditTab;
