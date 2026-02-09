import { useEffect, useState } from "react";

type HealthResponse = {
    status: string;
};

export default function App() {
    const [health, setHealth] = useState<string>("loading");
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchHealth = async () => {
            try {
                const response = await fetch("http://localhost:8000/health");
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }
                const data = (await response.json()) as HealthResponse;
                setHealth(data.status ?? "unknown");
                setError(null);
            } catch (err) {
                const message = err instanceof Error ? err.message : "Unknown error";
                setError(message);
                setHealth("error");
            }
        };

        fetchHealth();
    }, []);

    return (
        <div className="page">
            <h1>Frontend OK</h1>
            <p>
                Backend health: {error ? `error (${error})` : health}
            </p>
        </div>
    );
}
