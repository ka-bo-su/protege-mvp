export type ChatRole = "user" | "assistant" | "system";

export type ChatTurn = {
    id: string;
    role: ChatRole;
    content: string;
};

export type ChatTurnResponse = {
    session_id: string;
    assistant_message: string;
    turn_index: number;
};
