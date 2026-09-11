const NOTIFICATIONS_KEY = "freight_intelligence_notifications";

function getCurrentUserId() {
  try {
    const user = JSON.parse(
      localStorage.getItem("freight_intelligence_current_user")
    );

    return user?.id || null;
  } catch {
    return null;
  }
}

function getAllNotifications() {
  try {
    return (
      JSON.parse(localStorage.getItem(NOTIFICATIONS_KEY)) || []
    );
  } catch {
    return [];
  }
}

function saveAllNotifications(notifications) {
  localStorage.setItem(
    NOTIFICATIONS_KEY,
    JSON.stringify(notifications)
  );
}

export function getUserNotifications() {
  const userId = getCurrentUserId();

  if (!userId) return [];

  return getAllNotifications()
    .filter((notification) => notification.userId === userId)
    .sort(
      (a, b) =>
        new Date(b.createdAt) - new Date(a.createdAt)
    );
}

export function addNotification({
  type = "info",
  title,
  message,
  shipmentId = null,
}) {
  const userId = getCurrentUserId();

  if (!userId) return null;

  const notification = {
    id: crypto.randomUUID(),
    userId,
    type,
    title,
    message,
    shipmentId,
    read: false,
    createdAt: new Date().toISOString(),
  };

  const notifications = getAllNotifications();

  saveAllNotifications([
    notification,
    ...notifications,
  ]);

  window.dispatchEvent(
    new CustomEvent("freight-notifications-updated")
  );

  return notification;
}

export function markNotificationRead(id) {
  const userId = getCurrentUserId();

  if (!userId) return;

  const notifications = getAllNotifications();

  const updated = notifications.map((notification) => {
    if (
      notification.id === id &&
      notification.userId === userId
    ) {
      return {
        ...notification,
        read: true,
      };
    }

    return notification;
  });

  saveAllNotifications(updated);

  window.dispatchEvent(
    new CustomEvent("freight-notifications-updated")
  );
}

export function markAllNotificationsRead() {
  const userId = getCurrentUserId();

  if (!userId) return;

  const notifications = getAllNotifications();

  const updated = notifications.map((notification) => {
    if (notification.userId === userId) {
      return {
        ...notification,
        read: true,
      };
    }

    return notification;
  });

  saveAllNotifications(updated);

  window.dispatchEvent(
    new CustomEvent("freight-notifications-updated")
  );
}

export function getUnreadNotificationCount() {
  return getUserNotifications().filter(
    (notification) => !notification.read
  ).length;
}

export function deleteNotification(id) {
  const userId = getCurrentUserId();

  if (!userId) return;

  const notifications = getAllNotifications();

  const updated = notifications.filter(
    (notification) =>
      !(
        notification.id === id &&
        notification.userId === userId
      )
  );

  saveAllNotifications(updated);

  window.dispatchEvent(
    new CustomEvent("freight-notifications-updated")
  );
}

export function clearUserNotifications() {
  const userId = getCurrentUserId();

  if (!userId) return;

  const notifications = getAllNotifications();

  const remaining = notifications.filter(
    (notification) => notification.userId !== userId
  );

  saveAllNotifications(remaining);

  window.dispatchEvent(
    new CustomEvent("freight-notifications-updated")
  );
}