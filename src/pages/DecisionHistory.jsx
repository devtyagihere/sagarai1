import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  ArrowRight,
  CalendarDays,
  MapPin,
  Ship,
  Trash2,
} from "lucide-react";

import {
  getUserShipments,
  deleteShipment,
} from "../services/shipmentStorage";

export default function DecisionHistory() {
  const navigate = useNavigate();
  const [shipments, setShipments] = useState([]);

  const loadShipments = () => {
    setShipments(getUserShipments());
  };

  useEffect(() => {
    loadShipments();
  }, []);

  const handleDelete = (id) => {
    deleteShipment(id);
    loadShipments();
  };

  const formatDate = (date) => {
    if (!date) return "—";

    return new Date(date).toLocaleDateString("en-IN", {
      day: "2-digit",
      month: "short",
      year: "numeric",
    });
  };

  return (
    <div className="history-page">
      <div className="page-header">
        <div>
          <p className="section-label">SHIPMENT HISTORY</p>
          <h1>Your Voyage Decisions</h1>
          <p>
            Review shipments you have analysed and saved in your workspace.
          </p>
        </div>

        <button
          className="primary-action"
          onClick={() => navigate("/")}
        >
          New Shipment
          <ArrowRight size={17} />
        </button>
      </div>

      {shipments.length === 0 ? (
        <div className="history-empty">
          <div className="empty-icon">
            <Ship size={28} />
          </div>

          <h2>No shipments yet</h2>

          <p>
            Once you analyse a shipment, it will appear here automatically.
          </p>

          <button
            className="primary-action"
            onClick={() => navigate("/")}
          >
            Analyse Your First Shipment
            <ArrowRight size={17} />
          </button>
        </div>
      ) : (
        <div className="history-list">
          {shipments.map((shipment) => (
            <div className="history-card" key={shipment.id}>
              <div className="history-card-main">
                <div className="history-card-icon">
                  <Ship size={21} />
                </div>

                <div className="history-route">
                  <div className="route-label">
                    <MapPin size={14} />
                    VOYAGE
                  </div>

                  <h2>
                    {shipment.origin || "Unknown origin"}
                    <ArrowRight size={18} />
                    {shipment.destination || "Unknown destination"}
                  </h2>

                  <div className="history-meta">
                    <span>
                      {shipment.cargo || "Cargo not specified"}
                    </span>

                    <span>•</span>

                    <span>
                      {shipment.quantity
                        ? `${Number(shipment.quantity).toLocaleString()} MT`
                        : "Quantity not specified"}
                    </span>
                  </div>
                </div>
              </div>

              <div className="history-details">
                <div>
                  <span>DELIVERY</span>
                  <strong>
                    <CalendarDays size={14} />
                    {formatDate(shipment.deliveryDate)}
                  </strong>
                </div>

                <div>
                  <span>DURATION</span>
                  <strong>
                    {shipment.contractDuration || "—"} days
                  </strong>
                </div>

                <div>
                  <span>PRIORITY</span>
                  <strong>
                    {shipment.priority || "Normal"}
                  </strong>
                </div>

                <div>
                  <span>STATUS</span>
                  <strong className="history-status">
                    {shipment.status || "Analysed"}
                  </strong>
                </div>
              </div>

              <div className="history-actions">
                <button
                  type="button"
                  className="history-view"
                  onClick={() => navigate("/overview")}
                >
                  View
                  <ArrowRight size={16} />
                </button>

                <button
                  type="button"
                  className="history-delete"
                  title="Delete shipment"
                  onClick={() => handleDelete(shipment.id)}
                >
                  <Trash2 size={16} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}