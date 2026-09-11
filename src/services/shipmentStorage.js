const SHIPMENTS_KEY = "freight_intelligence_shipments";
const CURRENT_SHIPMENT_KEY = "freight_intelligence_current_shipment";

function getCurrentUserId() {
  try {
    const user = JSON.parse(
      localStorage.getItem(
        "freight_intelligence_current_user"
      )
    );

    return user?.id || null;
  } catch {
    return null;
  }
}

function getAllShipments() {
  try {
    return (
      JSON.parse(
        localStorage.getItem(SHIPMENTS_KEY)
      ) || []
    );
  } catch {
    return [];
  }
}

function saveAllShipments(shipments) {
  localStorage.setItem(
    SHIPMENTS_KEY,
    JSON.stringify(shipments)
  );
}

export function saveShipment(shipment) {
  const userId = getCurrentUserId();

  if (!userId) {
    throw new Error(
      "You must be logged in to save a shipment."
    );
  }

  const newShipment = {
    id: crypto.randomUUID(),

    userId,

    ...shipment,

    createdAt: new Date().toISOString(),

    status: "Analysed",
  };

  const shipments = getAllShipments();

  saveAllShipments([
    newShipment,
    ...shipments,
  ]);

  localStorage.setItem(
    CURRENT_SHIPMENT_KEY,
    JSON.stringify(newShipment)
  );

  return newShipment;
}

export function getUserShipments() {
  const userId = getCurrentUserId();

  if (!userId) {
    return [];
  }

  return getAllShipments().filter(
    (shipment) =>
      shipment.userId === userId
  );
}

export function getShipmentById(id) {
  const userId = getCurrentUserId();

  if (!userId) {
    return null;
  }

  return (
    getAllShipments().find(
      (shipment) =>
        shipment.id === id &&
        shipment.userId === userId
    ) || null
  );
}

export function getCurrentShipment() {
  const userId = getCurrentUserId();

  if (!userId) {
    return null;
  }

  const shipments = getUserShipments();

  return shipments.length > 0
    ? shipments[0]
    : null;
}

export function deleteShipment(id) {
  const userId = getCurrentUserId();

  if (!userId) {
    return false;
  }

  const shipments = getAllShipments();

  const updatedShipments =
    shipments.filter(
      (shipment) =>
        !(
          shipment.id === id &&
          shipment.userId === userId
        )
    );

  saveAllShipments(updatedShipments);

  return true;
}

export function clearUserShipments() {
  const userId = getCurrentUserId();

  if (!userId) {
    return;
  }

  const shipments = getAllShipments();

  const remainingShipments =
    shipments.filter(
      (shipment) =>
        shipment.userId !== userId
    );

  saveAllShipments(remainingShipments);

  localStorage.removeItem(
    CURRENT_SHIPMENT_KEY
  );
}
export function getShipment() {
  return getCurrentShipment();
}