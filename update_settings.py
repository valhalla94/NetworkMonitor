import re

with open('frontend/src/components/SettingsPage.jsx', 'r') as f:
    content = f.read()

# Imports
content = content.replace("import { Lock, ArrowLeft, Eye, EyeOff, Bell, Save } from 'lucide-react';",
                          "import { Lock, ArrowLeft, Eye, EyeOff, Bell, Save, Loader2 } from 'lucide-react';")

# States
content = content.replace("const [notificationMsg, setNotificationMsg] = useState('');",
                          "const [notificationMsg, setNotificationMsg] = useState('');\n    const [isLoggingIn, setIsLoggingIn] = useState(false);\n    const [isSaving, setIsSaving] = useState(false);")

# handleSaveNotification
old_save = """    const handleSaveNotification = async (e) => {
        e.preventDefault();
        try {
            await updateNotificationSettings(notificationUrl);
            setNotificationMsg('Settings saved and test notification sent!');
            setTimeout(() => setNotificationMsg(''), 5000);
        } catch {
            setNotificationMsg('Error saving settings.');
        }
    };"""

new_save = """    const handleSaveNotification = async (e) => {
        e.preventDefault();
        setIsSaving(true);
        try {
            await updateNotificationSettings(notificationUrl);
            setNotificationMsg('Settings saved and test notification sent!');
            setTimeout(() => setNotificationMsg(''), 5000);
        } catch {
            setNotificationMsg('Error saving settings.');
        } finally {
            setIsSaving(false);
        }
    };"""
content = content.replace(old_save, new_save)

# handleLogin
old_login = """    const handleLogin = async (e) => {
        e.preventDefault();
        try {
            const response = await login('admin', password);
            sessionStorage.setItem('token', response.data.access_token);
            setIsAuthenticated(true);
            setError('');
            setPassword('');
        } catch {
            setError('Incorrect password');
            setPassword('');
        }
    };"""

new_login = """    const handleLogin = async (e) => {
        e.preventDefault();
        setIsLoggingIn(true);
        try {
            const response = await login('admin', password);
            sessionStorage.setItem('token', response.data.access_token);
            setIsAuthenticated(true);
            setError('');
            setPassword('');
        } catch {
            setError('Incorrect password');
            setPassword('');
        } finally {
            setIsLoggingIn(false);
        }
    };"""
content = content.replace(old_login, new_login)


# Icons
content = content.replace('<Lock className="w-8 h-8 text-blue-400" />', '<Lock className="w-8 h-8 text-blue-400" aria-hidden="true" />')
content = content.replace('<Lock className="absolute left-3 top-3 w-5 h-5 text-slate-500" />', '<Lock className="absolute left-3 top-3 w-5 h-5 text-slate-500" aria-hidden="true" />')
content = content.replace('<Bell className="text-amber-400" />', '<Bell className="text-amber-400" aria-hidden="true" />')


# Unlock button
old_unlock_button = """                            <button type="submit" className="glass-button w-full py-3 rounded-xl font-bold text-lg flex items-center justify-center gap-2">
                                <Lock className="w-5 h-5" />
                                Unlock Settings
                            </button>"""
new_unlock_button = """                            <button type="submit" disabled={isLoggingIn} className="glass-button w-full py-3 rounded-xl font-bold text-lg flex items-center justify-center gap-2 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 disabled:opacity-50">
                                {isLoggingIn ? <Loader2 className="w-5 h-5 animate-spin" aria-hidden="true" /> : <Lock className="w-5 h-5" aria-hidden="true" />}
                                {isLoggingIn ? 'Unlocking...' : 'Unlock Settings'}
                            </button>"""
content = content.replace(old_unlock_button, new_unlock_button)

# Save button
old_save_button = """                                <button type="submit" className="glass-button px-6 py-2.5 rounded-xl font-bold text-lg flex items-center gap-2">
                                    <Save className="w-5 h-5" />
                                    Save & Test
                                </button>"""
new_save_button = """                                <button type="submit" disabled={isSaving} className="glass-button px-6 py-2.5 rounded-xl font-bold text-lg flex items-center gap-2 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 disabled:opacity-50">
                                    {isSaving ? <Loader2 className="w-5 h-5 animate-spin" aria-hidden="true" /> : <Save className="w-5 h-5" aria-hidden="true" />}
                                    {isSaving ? 'Saving...' : 'Save & Test'}
                                </button>"""
content = content.replace(old_save_button, new_save_button)

# Toggle password button
old_toggle = """                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    className="absolute right-3 top-3 text-slate-500 hover:text-slate-300 transition-colors"
                                    aria-label={showPassword ? "Hide password" : "Show password"}
                                    title={showPassword ? "Hide password" : "Show password"}
                                >
                                    {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                                </button>"""
new_toggle = """                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    className="absolute right-3 top-3 text-slate-500 hover:text-slate-300 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 rounded-lg"
                                    aria-label={showPassword ? "Hide password" : "Show password"}
                                    title={showPassword ? "Hide password" : "Show password"}
                                >
                                    {showPassword ? <EyeOff className="w-5 h-5" aria-hidden="true" /> : <Eye className="w-5 h-5" aria-hidden="true" />}
                                </button>"""
content = content.replace(old_toggle, new_toggle)


# Back to Dashboard button (login form)
old_back1 = """                            <button
                                type="button"
                                onClick={() => navigate('/')}
                                className="w-full py-3 rounded-xl font-medium text-slate-300 hover:text-white hover:bg-slate-800/30 transition-all flex items-center justify-center gap-2"
                            >
                                <ArrowLeft className="w-5 h-5" />
                                Back to Dashboard
                            </button>"""
new_back1 = """                            <button
                                type="button"
                                onClick={() => navigate('/')}
                                className="w-full py-3 rounded-xl font-medium text-slate-300 hover:text-white hover:bg-slate-800/30 transition-all flex items-center justify-center gap-2 focus:outline-none focus-visible:ring-2 focus-visible:ring-slate-500"
                            >
                                <ArrowLeft className="w-5 h-5" aria-hidden="true" />
                                Back to Dashboard
                            </button>"""
content = content.replace(old_back1, new_back1)


# Dashboard header button
old_back2 = """                        <button
                            onClick={() => navigate('/')}
                            className="px-4 py-2 rounded-xl font-medium text-slate-300 hover:text-white hover:bg-slate-800/30 transition-all flex items-center gap-2"
                        >
                            <ArrowLeft className="w-5 h-5" />
                            Dashboard
                        </button>"""
new_back2 = """                        <button
                            onClick={() => navigate('/')}
                            className="px-4 py-2 rounded-xl font-medium text-slate-300 hover:text-white hover:bg-slate-800/30 transition-all flex items-center gap-2 focus:outline-none focus-visible:ring-2 focus-visible:ring-slate-500"
                        >
                            <ArrowLeft className="w-5 h-5" aria-hidden="true" />
                            Dashboard
                        </button>"""
content = content.replace(old_back2, new_back2)


# Logout header button
old_logout = """                        <button
                            onClick={handleLogout}
                            className="px-4 py-2 rounded-xl font-medium bg-rose-500/10 text-rose-400 hover:bg-rose-500/20 transition-all flex items-center gap-2"
                        >
                            <Lock className="w-5 h-5" />
                            Logout
                        </button>"""
new_logout = """                        <button
                            onClick={handleLogout}
                            className="px-4 py-2 rounded-xl font-medium bg-rose-500/10 text-rose-400 hover:bg-rose-500/20 transition-all flex items-center gap-2 focus:outline-none focus-visible:ring-2 focus-visible:ring-rose-500"
                        >
                            <Lock className="w-5 h-5" aria-hidden="true" />
                            Logout
                        </button>"""
content = content.replace(old_logout, new_logout)


with open('frontend/src/components/SettingsPage.jsx', 'w') as f:
    f.write(content)
