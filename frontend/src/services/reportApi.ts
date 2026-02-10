import { request } from "../lib/api";
import type { ReportDraftResponse, ReportFinalResponse } from "../types/report";

type ReportFinalPayload = {
    report_final: string;
};

export async function generateReportDraft(sessionId: string): Promise<ReportDraftResponse> {
    return request<ReportDraftResponse>(`/api/v1/phase3/session/${sessionId}/report/draft`, {
        method: "POST",
    });
}

export async function saveReportFinal(sessionId: string, reportFinal: string): Promise<ReportFinalResponse> {
    const payload: ReportFinalPayload = { report_final: reportFinal };
    return request<ReportFinalResponse>(`/api/v1/phase3/session/${sessionId}/report/final`, {
        method: "PUT",
        body: JSON.stringify(payload),
    });
}
