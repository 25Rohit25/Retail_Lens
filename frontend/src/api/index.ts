const BASE_URL = "http://localhost:8000";

export const fetchMetrics = async (storeId: string) => {
  const res = await fetch(`${BASE_URL}/stores/${storeId}/metrics`);
  if (!res.ok) throw new Error("Failed to fetch metrics");
  return res.json();
};

export const fetchFunnel = async (storeId: string) => {
  const res = await fetch(`${BASE_URL}/stores/${storeId}/funnel`);
  if (!res.ok) throw new Error("Failed to fetch funnel");
  return res.json();
};

export const fetchAnomalies = async (storeId: string) => {
  const res = await fetch(`${BASE_URL}/stores/${storeId}/anomalies`);
  if (!res.ok) throw new Error("Failed to fetch anomalies");
  return res.json();
};
