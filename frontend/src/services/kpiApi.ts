import { request } from "../lib/api";
import type { EditRatioResponse } from "../types/kpi";

type EditRatioParams = {
    userId: number;
};

export async function fetchEditRatio({ userId }: EditRatioParams): Promise<EditRatioResponse> {
    return request<EditRatioResponse>(`/api/v1/kpi/edit-ratio?user_id=${userId}`);
}
