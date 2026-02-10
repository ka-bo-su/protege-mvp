import { useCallback, useRef, useState } from "react";
import type { RequestConfig, RequestResult, RequestState } from "../types/request";

const DEFAULT_ERROR_MESSAGE = "エラーが発生しました。再試行してください。";

type LastRequest<ActionType extends string, Payload, Result> = RequestConfig<ActionType, Payload, Result>;

type UseRequestControllerReturn<ActionType extends string, Payload> = {
    state: RequestState<ActionType>;
    run: <Result>(config: RequestConfig<ActionType, Payload, Result>) => Promise<RequestResult<ActionType, Payload, Result>>;
    retry: <Result>() => Promise<RequestResult<ActionType, Payload, Result>>;
    cancel: () => void;
    isCanceled: (requestId: number) => boolean;
};

export default function useRequestController<ActionType extends string, Payload>(): UseRequestControllerReturn<ActionType, Payload> {
    const [state, setState] = useState<RequestState<ActionType>>({ status: "idle" });
    const requestIdRef = useRef(0);
    const lastRequestRef = useRef<LastRequest<ActionType, Payload, unknown> | null>(null);

    const isCanceled = useCallback(
        (requestId: number) => requestId !== requestIdRef.current,
        []
    );

    const run = useCallback(
        async <Result,>(config: RequestConfig<ActionType, Payload, Result>): Promise<RequestResult<ActionType, Payload, Result>> => {
            if (state.status === "loading") {
                return { status: "skipped" };
            }

            const requestId = requestIdRef.current + 1;
            requestIdRef.current = requestId;
            lastRequestRef.current = config as LastRequest<ActionType, Payload, unknown>;

            setState({ status: "loading", actionType: config.actionType, requestId });

            try {
                const data = await config.requestFn(config.payload);
                if (requestId !== requestIdRef.current) {
                    return { status: "canceled", actionType: config.actionType, payload: config.payload, requestId };
                }
                setState({ status: "idle", actionType: config.actionType, requestId });
                return { status: "success", data, actionType: config.actionType, payload: config.payload, requestId };
            } catch (error) {
                if (requestId !== requestIdRef.current) {
                    return { status: "canceled", actionType: config.actionType, payload: config.payload, requestId };
                }
                const message = DEFAULT_ERROR_MESSAGE;
                setState({ status: "error", error: message, actionType: config.actionType, requestId });
                return { status: "error", error: message, actionType: config.actionType, payload: config.payload, requestId };
            }
        },
        [state.status]
    );

    const retry = useCallback(
        async <Result,>(): Promise<RequestResult<ActionType, Payload, Result>> => {
            const lastRequest = lastRequestRef.current as LastRequest<ActionType, Payload, Result> | null;
            if (!lastRequest) {
                return { status: "skipped" };
            }
            return run(lastRequest);
        },
        [run]
    );

    const cancel = useCallback(() => {
        requestIdRef.current += 1;
        setState((prev) => ({ status: "idle", actionType: prev.actionType }));
    }, []);

    return { state, run, retry, cancel, isCanceled };
}
