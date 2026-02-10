export type RequestStatus = "idle" | "loading" | "error";

export type RequestState<ActionType extends string = string> = {
    status: RequestStatus;
    error?: string;
    actionType?: ActionType;
    requestId?: number;
};

export type RequestConfig<ActionType extends string, Payload, Result> = {
    actionType: ActionType;
    payload: Payload;
    requestFn: (payload: Payload) => Promise<Result>;
};

export type RequestResult<ActionType extends string, Payload, Result> =
    | {
        status: "success";
        data: Result;
        actionType: ActionType;
        payload: Payload;
        requestId: number;
    }
    | {
        status: "error";
        error: string;
        actionType: ActionType;
        payload: Payload;
        requestId: number;
    }
    | {
        status: "canceled";
        actionType: ActionType;
        payload: Payload;
        requestId: number;
    }
    | {
        status: "skipped";
    };
