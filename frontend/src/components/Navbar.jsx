import { Link, useLocation } from 'react-router-dom';

export default function Navbar() {
    const location = useLocation();

    const isActive = (path) => location.pathname === path;

    return (
        <nav className="bg-white shadow-md border-b border-slate-200">
            <div className="container mx-auto px-6 py-4">
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                        <div className="w-10 h-10 bg-gradient-to-br from-primary-600 to-primary-800 rounded-lg flex items-center justify-center">
                            <svg
                                className="w-6 h-6 text-white"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                            >
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth={2}
                                    d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                                />
                            </svg>
                        </div>
                        <h1 className="text-xl font-bold bg-gradient-to-r from-primary-600 to-primary-800 bg-clip-text text-transparent">
                            Outbound Email Tracker
                        </h1>
                    </div>

                    <div className="flex space-x-1">
                        <Link
                            to="/"
                            className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 ${isActive('/')
                                ? 'bg-primary-100 text-primary-700'
                                : 'text-slate-600 hover:bg-slate-100'
                                }`}
                        >
                            Dashboard
                        </Link>
                        <Link
                            to="/leads"
                            className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 ${isActive('/leads')
                                ? 'bg-primary-100 text-primary-700'
                                : 'text-slate-600 hover:bg-slate-100'
                                }`}
                        >
                            Leads
                        </Link>
                        <Link
                            to="/send-email"
                            className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 ${isActive('/send-email')
                                ? 'bg-primary-100 text-primary-700'
                                : 'text-slate-600 hover:bg-slate-100'
                                }`}
                        >
                            Send Email
                        </Link>
                        <Link
                            to="/outbound-emails"
                            className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 ${isActive('/outbound-emails')
                                ? 'bg-primary-100 text-primary-700'
                                : 'text-slate-600 hover:bg-slate-100'
                                }`}
                        >
                            Outbound Emails
                        </Link>
                        <Link
                            to="/replies"
                            className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 ${isActive('/replies')
                                ? 'bg-primary-100 text-primary-700'
                                : 'text-slate-600 hover:bg-slate-100'
                                }`}
                        >
                            Replies Inbox
                        </Link>
                    </div>
                </div>
            </div>
        </nav>
    );
}
