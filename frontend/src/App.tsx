/**
 * HCPilot AI — Main Application Component
 * Split-screen layout: FormPanel (left) + ChatPanel (right)
 */
import { Provider } from "react-redux";
import { store } from "./redux/store";
import FormPanel from "./components/FormPanel/FormPanel";
import ChatPanel from "./components/ChatPanel/ChatPanel";
import "./App.css";

function AppContent() {
  return (
    <div className="app">
      {/* Top Header Bar */}
      <header className="app-header">
        <div className="app-brand">
          <div className="app-logo">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
            </svg>
          </div>
          <div className="app-brand-text">
            <span className="app-name">HCPilot<span className="app-name-accent">AI</span></span>
            <span className="app-tagline">AI-First CRM for Healthcare</span>
          </div>
        </div>
        <div className="app-header-right">
          <div className="status-dot" />
          <span className="status-text">Connected</span>
        </div>
      </header>

      {/* Split Screen Layout */}
      <main className="app-main">
        <div className="panel panel-left">
          <FormPanel />
        </div>
        <div className="panel panel-right">
          <ChatPanel />
        </div>
      </main>
    </div>
  );
}

function App() {
  return (
    <Provider store={store}>
      <AppContent />
    </Provider>
  );
}

export default App;
