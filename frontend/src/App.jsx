/**
 * App.jsx — top-level shell.
 *
 * Layout: Sidebar | [StatusBar + active view] | SourcePanel (chat mode only)
 *
 * Provider tracking: the StatusBar only shows the provider once the backend
 * has confirmed it via a ChatResponse. It is never assumed or fabricated.
 */

import { useState, useCallback, useEffect } from "react";
import { fetchSessions, fetchProviders } from "./services/api";
import Sidebar     from "./components/Sidebar";
import StatusBar   from "./components/StatusBar";
import ChatView    from "./components/ChatView";
import SearchView  from "./components/SearchView";
import Ship30View  from "./components/Ship30View";
import ArtifactView from "./components/ArtifactView";
import SourcePanel from "./components/SourcePanel";
import styles      from "./App.module.css";

export default function App() {
  const [mode,       setMode]       = useState("chat");
  const [sessionId,  setSessionId]  = useState(null);
  const [provider,   setProvider]   = useState(null);   // set by ChatView
  const [selectedProvider, setSelectedProvider] = useState("ollama");
  const [chatSources, setChatSources] = useState([]);
  // Increment to force-remount ChatView (resets hook state for new chat).
  const [chatKey,    setChatKey]    = useState(0);
  const [sessions, setSessions] = useState([]);
  const [providers, setProviders] = useState([]);
  const [defaultProvider, setDefaultProvider] = useState("ollama");
  const [selectSession, setSelectSession] = useState(null);
  const [artifact, setArtifact] = useState(null);
  const [rightPane, setRightPane] = useState("evidence");
  const refreshSessions = useCallback(async () => { try { setSessions(await fetchSessions()); } catch { /* Status bar reflects backend health. */ } }, []);
  useEffect(() => {
    fetchSessions().then(setSessions).catch(() => {});
    fetchProviders().then((x) => { setProviders(x.providers); setDefaultProvider(x.default); }).catch(() => { setProviders([{id:"ollama",available:true,model:"qwen2.5:3b"}]); setDefaultProvider("ollama"); });
  }, []);
  const switchSession = useCallback((id) => { setSessionId(id); selectSession?.(id); setMode("chat"); }, [selectSession]);

  const handleSourcesUpdate = useCallback((sources) => {
    setChatSources(sources);
  }, []);

  const handleNewChat = useCallback(() => {
    setSessionId(null);
    setProvider(null);
    setChatSources([]);
    setChatKey((k) => k + 1);
  }, []);
  const openArtifactBesideChat = useCallback((value) => { if (value) setArtifact(value); setRightPane("artifact"); setMode("chat"); }, []);

  return (
    <div className={styles.app}>
      <Sidebar
        activeMode={mode}
        onModeChange={setMode}
        onNewChat={handleNewChat}
        sessionId={sessionId}
        sessions={sessions}
        onSelectSession={switchSession}
      />

      <div className={styles.main}>
        {/* StatusBar only shows provider when backend confirms it */}
        <StatusBar provider={provider} />

        <div className={styles.content}>
          {mode === "chat" && (
            <>
              <ChatView
                key={chatKey}
                onSessionChange={setSessionId}
                onProviderChange={setProvider}
                onSelectedProviderChange={setSelectedProvider}
                onSourcesUpdate={handleSourcesUpdate}
                onSessionListChange={refreshSessions}
                onSelectSession={setSelectSession}
                onProviderOptions={providers}
                defaultProvider={defaultProvider}
              />
              {rightPane === "artifact" && artifact ? <ArtifactView compact artifact={artifact} sessionId={sessionId} provider={selectedProvider} /> : <SourcePanel
                results={chatSources}
                isLoading={false}
                error={null}
                artifactOpen={rightPane === "artifact"}
                hasArtifact={Boolean(artifact)}
                onShowEvidence={() => setRightPane("evidence")}
                onShowArtifact={() => setRightPane("artifact")}
              />}
            </>
          )}

          {mode === "search"    && <SearchView />}
          {mode === "ship30"    && <Ship30View sessionId={sessionId} provider={selectedProvider} onArtifact={setArtifact} onOpenArtifact={openArtifactBesideChat} />}
          {mode === "artifacts" && <ArtifactView sessionId={sessionId} provider={selectedProvider} artifact={artifact} onArtifact={setArtifact} onOpenInChat={openArtifactBesideChat} />}
        </div>
      </div>
    </div>
  );
}
