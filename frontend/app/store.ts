import {create} from "zustand"
import {persist} from "zustand/middleware"


type WorkspaceSettings = {
    use_hyde: boolean;
    use_bm25:boolean;
    top_k: number;
};

const default_ws_settings = {
    use_bm25: false,
    use_hyde: false,
    top_k: 20,
}

type AppState = {
    ws_id: string | null;
    chat_id: string | null;
    workspace_settings: Record<string,WorkspaceSettings>;

    set_active_chat: (ws_id:string|null,chat_id:string|null) => void;
    set_bm25: (val:boolean,ws_id:string) => void;
    set_hyde: (val:boolean,ws_id:string) => void;
    set_top_k: (val:number,ws_id:string) => void;
};

export const useAppStore = create<AppState>()(
    persist(
        (set) => ({
            workspace_settings: {},
            ws_id: null,
            chat_id: null,

            set_active_chat: (ws_id,chat_id) =>
                set({
                    ws_id,chat_id,
                }),
            set_bm25: (val,ws_id) => 
                set((state) => ({
                    workspace_settings: {
                        ...state.workspace_settings,
                        [ws_id]: {
                            ...state.workspace_settings[ws_id],
                            use_bm25: val
                        }
                    }
                })),
            set_hyde: (val,ws_id) => 
                set((state) => ({
                    workspace_settings: {
                        ...state.workspace_settings,
                        [ws_id]: {
                            ...state.workspace_settings[ws_id],
                            use_hyde: val
                        }
                    }
                })),
            set_top_k: (val,ws_id) => 
                set((state) => ({
                    workspace_settings: {
                        ...state.workspace_settings,
                        [ws_id]: {
                            ...state.workspace_settings[ws_id],
                            top_k: val
                        }
                    }
                })),
        }),
        {
            name: "rag-app-state",
        }
    )
)