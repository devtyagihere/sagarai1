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
  localStorage.removeItem("maritime_analysis_result");
}

export function saveAnalysisResult(result) {
  localStorage.setItem(
    "maritime_analysis_result",
    JSON.stringify(result)
  );
}

export function getAnalysisResult() {
  const savedResult = localStorage.getItem("maritime_analysis_result");

  if (!savedResult) {
    return null;
  }

  try {
    return JSON.parse(savedResult);
  } catch {
    return null;
  }
}