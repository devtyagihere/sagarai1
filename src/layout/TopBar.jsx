import { useEffect, useState } from "react";
import {
  Bell,
  Check,
  CircleUserRound,
  Menu,
  Ship,
  X,
} from "lucide-react";
import { useNavigate } from "react-router-dom";

import {
  deleteNotification,
  getUnreadNotificationCount,
  getUserNotifications,
  markAllNotificationsRead,
  markNotificationRead,
} from "../services/notificationStorage";

export default function TopBar({
  onMenuClick,
  user,
  onLogout,
}) {
  const navigate = useNavigate();

  const [notifications, setNotifications] = useState([]);
  const [notificationOpen, setNotificationOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);

  const loadNotifications = () => {
    setNotifications(getUserNotifications());
  };

  useEffect(() => {
    loadNotifications();

    const handleUpdate = () => {
      loadNotifications();
    };

    window.addEventListener(
      "freight-notifications-updated",
      handleUpdate
    );

    return () => {
      window.removeEventListener(
        "freight-notifications-updated",
        handleUpdate
      );
    };
  }, []);

  const unreadCount = getUnreadNotificationCount();

  const handleNotificationClick = (notification) => {
    markNotificationRead(notification.id);

    setNotificationOpen(false);

    if (notification.shipmentId) {
      navigate("/overview");
    }
  };

  const handleMarkAllRead = () => {
    markAllNotificationsRead();
    loadNotifications();
  };

  const handleDeleteNotification = (event, id) => {
    event.stopPropagation();

    deleteNotification(id);
    loadNotifications();
  };

  const handleHistoryClick = () => {
    setProfileOpen(false);
    navigate("/history");
  };

  const handleNotificationsClick = () => {
    setProfileOpen(false);
    setNotificationOpen(true);
  };

  const handleLogout = () => {
    setProfileOpen(false);
    setNotificationOpen(false);
    onLogout();
  };

  const formatTime = (createdAt) => {
    const created = new Date(createdAt);
    const now = new Date();

    const difference = Math.floor(
      (now - created) / 1000
    );

    if (difference < 60) {
      return "Just now";
    }

    const minutes = Math.floor(difference / 60);

    if (minutes < 60) {
      return `${minutes}m ago`;
    }

    const hours = Math.floor(minutes / 60);

    if (hours < 24) {
      return `${hours}h ago`;
    }

    return created.toLocaleDateString("en-IN", {
      day: "2-digit",
      month: "short",
    });
  };

  return (
    <header className="topbar">

      {/* LEFT */}

      <div className="topbar-left">

        <button
          className="mobile-menu-button"
          onClick={onMenuClick}
          type="button"
          aria-label="Open navigation"
        >
          <Menu size={21} />
        </button>

        <div className="topbar-title">
          Freight Intelligence
        </div>

      </div>


      {/* RIGHT */}

      <div className="topbar-actions">

        {/* CONNECTION */}

        <div className="connection-status">
          <span className="connection-dot" />
          <span>Live workspace</span>
        </div>


        {/* NOTIFICATIONS */}

        <div className="topbar-dropdown-wrapper">

          <button
            className="topbar-icon-button"
            type="button"
            aria-label="Notifications"
            onClick={() => {
              setNotificationOpen(
                (current) => !current
              );
              setProfileOpen(false);
            }}
          >
            <Bell size={19} />

            {unreadCount > 0 && (
              <span className="notification-badge">
                {unreadCount > 9
                  ? "9+"
                  : unreadCount}
              </span>
            )}
          </button>


          {notificationOpen && (
            <div className="notification-dropdown">

              <div className="notification-header">

                <div>
                  <strong>
                    Notifications
                  </strong>

                  <span>
                    {unreadCount > 0
                      ? `${unreadCount} unread`
                      : "All caught up"}
                  </span>
                </div>

                {unreadCount > 0 && (
                  <button
                    className="mark-read-button"
                    type="button"
                    onClick={handleMarkAllRead}
                  >
                    <Check size={14} />
                    Mark all read
                  </button>
                )}

              </div>


              <div className="notification-list">

                {notifications.length === 0 ? (
                  <div className="notification-empty">

                    <Bell size={28} />

                    <strong>
                      No notifications yet
                    </strong>

                    <p>
                      Notifications will appear here
                      when you analyse shipments or
                      complete workspace actions.
                    </p>

                  </div>
                ) : (
                  notifications.map(
                    (notification) => (
                      <div
                        key={notification.id}
                        className={`notification-item ${
                          !notification.read
                            ? "notification-unread"
                            : ""
                        }`}
                        onClick={() =>
                          handleNotificationClick(
                            notification
                          )
                        }
                        role="button"
                        tabIndex={0}
                        onKeyDown={(event) => {
                          if (
                            event.key === "Enter"
                          ) {
                            handleNotificationClick(
                              notification
                            );
                          }
                        }}
                      >

                        <div className="notification-icon">

                          {notification.type ===
                          "shipment" ? (
                            <Ship size={17} />
                          ) : (
                            <Bell size={17} />
                          )}

                        </div>


                        <div className="notification-content">

                          <div className="notification-title-row">

                            <strong>
                              {notification.title}
                            </strong>

                            <button
                              className="notification-delete"
                              type="button"
                              aria-label="Delete notification"
                              onClick={(event) =>
                                handleDeleteNotification(
                                  event,
                                  notification.id
                                )
                              }
                            >
                              <X size={13} />
                            </button>

                          </div>

                          <p>
                            {notification.message}
                          </p>

                          <span>
                            {formatTime(
                              notification.createdAt
                            )}
                          </span>

                        </div>


                        {!notification.read && (
                          <span className="notification-unread-dot" />
                        )}

                      </div>
                    )
                  )
                )}

              </div>

            </div>
          )}

        </div>


        {/* PROFILE */}

        <div className="topbar-dropdown-wrapper">

          <button
            className="profile-button"
            type="button"
            onClick={() => {
              setProfileOpen(
                (current) => !current
              );
              setNotificationOpen(false);
            }}
          >

            <CircleUserRound size={20} />

            <span>
              {user?.name || "User"}
            </span>

          </button>


          {profileOpen && (
            <div className="profile-dropdown">

              <div className="profile-header">

                <div className="profile-avatar">
                  {(user?.name || "U")
                    .charAt(0)
                    .toUpperCase()}
                </div>

                <div className="profile-info">

                  <strong>
                    {user?.name || "User"}
                  </strong>

                  <span>
                    {user?.email || ""}
                  </span>

                </div>

              </div>


              <div className="profile-divider" />


              <button
                type="button"
                onClick={handleHistoryClick}
              >
                <Ship size={16} />
                Shipment History
              </button>


              <button
                type="button"
                onClick={handleNotificationsClick}
              >
                <Bell size={16} />
                Notifications

                {unreadCount > 0 && (
                  <span className="profile-notification-count">
                    {unreadCount}
                  </span>
                )}
              </button>


              <div className="profile-divider" />


              <button
                className="profile-signout"
                type="button"
                onClick={handleLogout}
              >
                Sign out
              </button>

            </div>
          )}

        </div>

      </div>

    </header>
  );
}