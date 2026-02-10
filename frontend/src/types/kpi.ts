export type EditRatioItem = {
    session_id: string;
    session_date: string;
    ratio: number;
    chars_added: number;
    chars_removed: number;
};

export type EditRatioSummary = {
    count: number;
    avg: number | null;
    median: number | null;
    min: number | null;
    max: number | null;
};

export type EditRatioResponse = {
    user_id: number;
    items: EditRatioItem[];
    summary: EditRatioSummary;
};
