import React from "react";
import { Box, Stack, Avatar, Typography } from "@mui/material";
import botIcon from "../../assets/icons/botIcon.svg";
import styles from "./SCNInternalReviewAuditTab.module.scss";

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

// --- Sample Data ---
const timelineData: TimelineEvent[] = [
  {
    id: 1,
    type: "approved",
    timestamp: "JAN 10, 11:50 AM",
    title: "SCN-INT-000234 Approved",
    description:
      "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore.",
  },
  {
    id: 2,
    type: "rejected",
    timestamp: "JAN 20, 12:20 AM",
    title: "SCN-INT-000234 Info requested",
    description:
      "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore.",
  },
  {
    id: 3,
    type: "review",
    timestamp: "JAN 2, 11:50 AM",
    title: "SCN-INT-000234 Under review",
    description:
      "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore.",
  },
  {
    id: 4,
    type: "edited",
    timestamp: "JAN 1, 10:15 AM",
    title: "SCN-INT-000234 record edited", // Note: Display logic might reconstruct this
    description:
      "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore.",
    user: {
      name: "Earl Johnson",
      email: "carolskoney@mail.com",
      avatar: "/avatar.png",
    },
  },
  {
    id: 5,
    type: "created", // Assumed from context of "Created"
    timestamp: "Dec 29, 09:15 PM",
    title: "SCN-INT-000234 record", // "Created SCN-INT-000234 record"
    description:
      "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore.",
    user: {
      name: "Earl Johnson",
      email: "carolskoney@mail.com",
      avatar: "/avatar.png",
    },
  },
];

// --- Components ---

const TimelineItem = ({
  item,
  isLast,
}: {
  item: TimelineEvent;
  isLast: boolean;
}) => {
  const { type, timestamp, title, description, user } = item;

  // Render logic for different content types
  const renderContentHeader = () => {
    if (user) {
      const isCreate = type === "created";
      const actionText = isCreate ? "Created" : "has edited the file";
      const objectText = title
        .replace(" record edited", "")
        .replace(" record", "");
      const fullObjectText = `SCN-INT-000234 record`;

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
                  {type === "created" ? title : "SCN-INT-000234 record"}
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
          isLast={index === data.length}
        />
      ))}
    </Box>
  );
};

const SCNInternalReviewAuditTab = () => {
  return (
    <Box>
      <ActivityTimeline data={timelineData} />
    </Box>
  );
};

export default SCNInternalReviewAuditTab;
