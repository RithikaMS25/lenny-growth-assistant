/**
 * Sidebar — branding, new-chat button, session info, mode navigation.
 */

import styles from "./Sidebar.module.css";

const NAV_ITEMS = [
  { id: "chat", label: "Ask Lenny", icon: "💬" },
  { id: "search", label: "Source Search", icon: "🔍" },
  { id: "ship30", label: "Ship 30 for 30", icon: "✍️" },
  { id: "artifacts", label: "Documents", icon: "📄" },
];

export default function Sidebar({ activeMode, onModeChange, onNewChat, sessionId, sessions = [], onSelectSession }) {
  return (
    <aside className={styles.sidebar}>
      {/* Branding */}
      <div className={styles.brand}>
        <div className={styles.brandIcon}>L</div>
        <div className={styles.brandText}>
          <span className={styles.brandTitle}>Lenny</span>
          <span className={styles.brandSub}>Growth Assistant</span>
        </div>
      </div>

      {/* New Chat */}
      <button
        className={styles.newChatBtn}
        onClick={onNewChat}
        aria-label="Start a new chat session"
      >
        <span className={styles.newChatIcon}>+</span>
        New Chat
      </button>

      {/* Navigation */}
      <nav className={styles.nav} aria-label="Main navigation">
        {NAV_ITEMS.map((item) => (
          <button
            key={item.id}
            className={`${styles.navItem} ${activeMode === item.id ? styles.navItemActive : ""}`}
            onClick={() => onModeChange(item.id)}
            aria-current={activeMode === item.id ? "page" : undefined}
          >
            <span className={styles.navIcon}>{item.icon}</span>
            <span className={styles.navLabel}>{item.label}</span>
          </button>
        ))}
      </nav>

      <div className={styles.sessionList} aria-label="Chat history">
        <span className={styles.sessionText}>Recent chats</span>
        {sessions.map((item) => <button key={item.id} className={`${styles.navItem} ${sessionId === item.id ? styles.navItemActive : ""}`} title={item.title} onClick={() => onSelectSession?.(item.id)}>{item.title || "New conversation"}</button>)}
        {!sessions.length && <span className={styles.sessionText}>No saved chats yet</span>}
      </div>

      {/* Session info */}
      <div className={styles.sessionInfo}>
        {sessionId ? (
          <>
            <span className={styles.sessionDot} title="Session active" />
            <span className={styles.sessionText}>
              Session: {sessionId.slice(0, 8)}…
            </span>
          </>
        ) : (
          <span className={styles.sessionText}>No active session</span>
        )}
      </div>
    </aside>
  );
}
