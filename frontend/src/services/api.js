import { saveShipment, saveAnalysisResult } from "./shipmentStorage";

export async function analyzeShipment(formData) {
  let cargoType = (formData.cargo || "").trim().toLowerCase().replace(/\s+/g, "_");
  if (cargoType === "steel") cargoType = "steel_coils";
  if (cargoType === "other_bulk_cargo") cargoType = "iron_ore";

  const payload = {
    cargo_type: cargoType,
    cargo_quantity_tonnes: Number(formData.quantity),
    origin_port: formData.origin.trim(),
    destination_port: formData.destination.trim(),
    shipping_deadline_days: formData.contractDuration ? Number(formData.contractDuration) : null,
  };

  const response = await fetch("/api/analyze", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    let errorMsg = "Analysis failed";
    try {
      const err = await response.json();
      errorMsg = err.detail || err.message || errorMsg;
    } catch {
      errorMsg = "Server error (" + response.status + ")";
    }
    throw new Error(errorMsg);
  }

  const data = await response.json();
  saveShipment(formData);
  saveAnalysisResult(data);
  return data;
}

export async function fetchMarketSnapshot(cargoType = null) {
  try {
    const url = cargoType ? "/api/market/snapshot?cargo_type=" + encodeURIComponent(cargoType) : "/api/market/snapshot";
    const response = await fetch(url);
    if (!response.ok) return null;
    return await response.json();
  } catch {
    return null;
  }
}

export async function fetchPortOperations() {
  try {
    const response = await fetch("/api/port-operations");
    if (!response.ok) return [];
    return await response.json();
  } catch {
    return [];
  }
}

export async function fetchPorts() {
  try {
    const response = await fetch("/api/ports");
    if (!response.ok) return [];
    return await response.json();
  } catch {
    return [];
  }
}
