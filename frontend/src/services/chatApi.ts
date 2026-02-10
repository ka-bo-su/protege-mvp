import { request } from "../lib/api";
import type { ChatTurnResponse } from "../types/chat";

export async function sendPhase1Turn(sessionId: string, message: string): Promise<ChatTurnResponse> {
    return request<ChatTurnResponse>(`/api/v1/phase1/session/${sessionId}/turn`, {
        method: "POST",
        body: JSON.stringify({ message }),
    });
}

export async function sendPhase3Turn(sessionId: string, message: string): Promise<ChatTurnResponse> {
    return request<ChatTurnResponse>(`/api/v1/phase3/session/${sessionId}/turn`, {
        method: "POST",
        body: JSON.stringify({ message }),
    });
}
