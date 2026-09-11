const STORAGE_KEY = "maritime_shipment";

export function saveShipment(shipment) {
  localStorage.setItem(
    STORAGE_KEY,
    JSON.stringify(shipment)
  );
}

export function getShipment() {
  const savedShipment = localStorage.getItem(STORAGE_KEY);

  if (!savedShipment) {
    return null;
  }

  try {
    return JSON.parse(savedShipment);
  } catch {
    return null;
  }
}

export function clearShipment() {
  localStorage.removeItem(STORAGE_KEY);
}