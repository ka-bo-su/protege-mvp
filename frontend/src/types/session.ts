export type SessionPhase = 1 | 3;

export type SessionSummary = {
    id: string;
    phase: SessionPhase;
    session_date: string;
};

export type SessionCreateResponse = {
    id: string;
    phase?: SessionPhase;
    session_date?: string;
};
