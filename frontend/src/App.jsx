import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import Leads from './pages/Leads';
import SendEmail from './pages/SendEmail';
import OutboundEmails from './pages/OutboundEmails';
import RepliesInbox from './pages/RepliesInbox';
import './index.css';

function App() {
  return (
    <Router>
      <div className="min-h-screen">
        <Navbar />
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/leads" element={<Leads />} />
          <Route path="/send-email" element={<SendEmail />} />
          <Route path="/outbound-emails" element={<OutboundEmails />} />
          <Route path="/replies" element={<RepliesInbox />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
