export type EditMetrics = {
    chars_added: number;
    chars_removed: number;
    ratio: number;
};

export type ReportDraftResponse = {
    session_id: string;
    report_draft: string;
    saved: boolean;
};

export type ReportFinalResponse = {
    session_id: string;
    saved: boolean;
    edit_metrics: EditMetrics;
};
