const DEFAULT_BASE_URL = "http://localhost:8000";

export const baseUrl = import.meta.env.VITE_API_BASE_URL ?? DEFAULT_BASE_URL;

type ApiErrorInfo = {
    status: number;
    message: string;
};

export async function request<T>(path: string, init?: RequestInit): Promise<T> {
    const response = await fetch(`${baseUrl}${path}`, {
        headers: {
            "Content-Type": "application/json",
            ...(init?.headers ?? {}),
        },
        ...init,
    });

    if (!response.ok) {
        const error: ApiErrorInfo = {
            status: response.status,
            message: response.statusText || `HTTP ${response.status}`,
        };
        throw new Error(`${error.status}: ${error.message}`);
    }

    return (await response.json()) as T;
}

export type HealthResponse = {
    status: string;
};

export async function getHealth(): Promise<HealthResponse> {
    return request<HealthResponse>("/health");
}
