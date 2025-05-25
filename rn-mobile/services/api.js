const API_URL = "http://localhost:8000"; // Replace with your IP or ngrok URL if testing on a device

export const getAllDivestments = async () => {
  const res = await fetch(`${API_URL}/divestments_main`, {
    headers: {
      Authorization: "Bearer <your_token_here>", // Use real token if auth is needed
    },
  });

  if (!res.ok) throw new Error("Failed to fetch divestments");
  return await res.json();
};
