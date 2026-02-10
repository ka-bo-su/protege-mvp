import { request } from "../lib/api";
import type { SessionCreateResponse, SessionPhase, SessionSummary } from "../types/session";

type ListSessionsParams = {
    userId: number;
};

export async function fetchSessions({ userId }: ListSessionsParams): Promise<SessionSummary[]> {
    return request<SessionSummary[]>(`/api/v1/sessions?user_id=${userId}`);
}

export async function createSession(phase: SessionPhase): Promise<SessionCreateResponse> {
    const path = phase === 1 ? "/api/v1/phase1/session" : "/api/v1/phase3/session";
    return request<SessionCreateResponse>(path, {
        method: "POST",
    });
}
