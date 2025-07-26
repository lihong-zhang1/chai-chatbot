/**
 * CHAI Chatbot Interface - Elegant JavaScript Implementation
 * Crafted with attention to detail and user experience
 */

class ChatInterface {
    constructor() {
        this.isLoading = false;
        this.config = {
            botName: 'Assistant',
            userName: 'User',
            customPrompt: ''
        };
        
        this.initializeElements();
        this.setupEventListeners();
        this.loadConfiguration();
        this.setWelcomeTime();
    }
    
    initializeElements() {
        // Core elements
        this.messagesContainer = document.getElementById('messages');
        this.messageInput = document.getElementById('message-input');
        this.sendButton = document.getElementById('send-btn');
        this.loadingIndicator = document.getElementById('loading');
        this.charCount = document.getElementById('char-count');
        
        // Header elements
        this.botNameElement = document.getElementById('bot-name');
        this.clearChatButton = document.getElementById('clear-chat');
        this.settingsButton = document.getElementById('settings-btn');
        
        // Modal elements
        this.settingsModal = document.getElementById('settings-modal');
        this.closeSettingsButton = document.getElementById('close-settings');
        this.userNameInput = document.getElementById('user-name-input');
        this.botNameInput = document.getElementById('bot-name-input');
        this.customPromptInput = document.getElementById('custom-prompt');
        this.saveSettingsButton = document.getElementById('save-settings');
        this.resetSettingsButton = document.getElementById('reset-settings');
        
        // Toast container
        this.toastContainer = document.getElementById('toast-container');
    }
    
    setupEventListeners() {
        // Input events
        this.messageInput.addEventListener('input', () => this.handleInputChange());
        this.messageInput.addEventListener('keydown', (e) => this.handleKeyDown(e));
        this.sendButton.addEventListener('click', () => this.sendMessage());
        
        // Header actions
        this.clearChatButton.addEventListener('click', () => this.clearChat());
        this.settingsButton.addEventListener('click', () => this.openSettings());
        
        // Modal events
        this.closeSettingsButton.addEventListener('click', () => this.closeSettings());
        this.saveSettingsButton.addEventListener('click', () => this.saveSettings());
        this.resetSettingsButton.addEventListener('click', () => this.resetSettings());
        
        // Close modal on overlay click
        this.settingsModal.addEventListener('click', (e) => {
            if (e.target === this.settingsModal) {
                this.closeSettings();
            }
        });
        
        // Auto-resize textarea
        this.messageInput.addEventListener('input', () => this.autoResizeTextarea());
        
        // Escape key to close modal
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.settingsModal.classList.contains('show')) {
                this.closeSettings();
            }
        });
    }
    
    async loadConfiguration() {
        try {
            const response = await fetch('/api/config');
            if (response.ok) {
                const config = await response.json();
                this.config.botName = config.bot_name;
                this.config.userName = config.user_name;
                this.updateUI();
            }
        } catch (error) {
            console.error('Failed to load configuration:', error);
            this.showToast('Failed to load configuration', 'error');
        }
    }
    
    setWelcomeTime() {
        const welcomeTimeElement = document.getElementById('welcome-time');
        if (welcomeTimeElement) {
            welcomeTimeElement.textContent = this.formatTime(new Date());
        }
    }
    
    updateUI() {
        this.botNameElement.textContent = this.config.botName;
        this.userNameInput.value = this.config.userName;
        this.botNameInput.value = this.config.botName;
    }
    
    handleInputChange() {
        const message = this.messageInput.value.trim();
        const charLength = this.messageInput.value.length;
        
        this.charCount.textContent = charLength;
        this.sendButton.disabled = !message || this.isLoading;
        
        // Update character count color
        if (charLength > 1800) {
            this.charCount.style.color = '#ef4444';
        } else if (charLength > 1500) {
            this.charCount.style.color = '#f59e0b';
        } else {
            this.charCount.style.color = '#94a3b8';
        }
    }
    
    handleKeyDown(event) {
        if (event.key === 'Enter') {
            if (event.shiftKey) {
                // Allow new line with Shift+Enter
                return;
            } else {
                // Send message with Enter
                event.preventDefault();
                if (!this.sendButton.disabled) {
                    this.sendMessage();
                }
            }
        }
    }
    
    autoResizeTextarea() {
        const textarea = this.messageInput;
        textarea.style.height = 'auto';
        const newHeight = Math.min(textarea.scrollHeight, 120);
        textarea.style.height = newHeight + 'px';
    }
    
    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message || this.isLoading) return;
        
        this.setLoading(true);
        
        // Add user message to UI immediately
        this.addMessage(message, this.config.userName, true);
        this.messageInput.value = '';
        this.messageInput.style.height = 'auto';
        this.handleInputChange();
        
        try {
            const requestBody = {
                message: message,
                bot_name: this.config.botName,
                user_name: this.config.userName
            };
            
            if (this.config.customPrompt) {
                requestBody.custom_prompt = this.config.customPrompt;
            }
            
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody)
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.addMessage(data.response, data.bot_name, false);
            } else {
                this.showToast(data.error || 'Failed to send message', 'error');
                // Add error message to chat
                this.addMessage(
                    'Sorry, I encountered an error processing your message. Please try again.',
                    this.config.botName,
                    false,
                    true
                );
            }
        } catch (error) {
            console.error('Error sending message:', error);
            this.showToast('Network error. Please check your connection.', 'error');
            this.addMessage(
                'Sorry, I\'m having trouble connecting. Please try again.',
                this.config.botName,
                false,
                true
            );
        } finally {
            this.setLoading(false);
        }
    }
    
    addMessage(content, sender, isUser, isError = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = isUser ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        const messageBubble = document.createElement('div');
        messageBubble.className = 'message-bubble';
        if (isError) {
            messageBubble.style.opacity = '0.7';
            messageBubble.style.fontStyle = 'italic';
        }
        
        // Process message content for better formatting
        const formattedContent = this.formatMessageContent(content);
        messageBubble.innerHTML = formattedContent;
        
        const messageTime = document.createElement('div');
        messageTime.className = 'message-time';
        messageTime.textContent = this.formatTime(new Date());
        
        messageContent.appendChild(messageBubble);
        messageContent.appendChild(messageTime);
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageContent);
        
        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    formatMessageContent(content) {
        // Convert line breaks to HTML
        return content
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>');
    }
    
    formatTime(date) {
        return date.toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
    }
    
    scrollToBottom() {
        const messagesWrapper = this.messagesContainer.parentElement;
        messagesWrapper.scrollTop = messagesWrapper.scrollHeight;
    }
    
    setLoading(loading) {
        this.isLoading = loading;
        this.sendButton.disabled = loading || !this.messageInput.value.trim();
        
        if (loading) {
            this.loadingIndicator.classList.add('show');
        } else {
            this.loadingIndicator.classList.remove('show');
        }
    }
    
    async clearChat() {
        if (!confirm('Are you sure you want to clear the chat history?')) {
            return;
        }
        
        try {
            const response = await fetch('/api/clear', { method: 'POST' });
            const data = await response.json();
            
            if (data.success) {
                // Keep only the welcome message
                const welcomeMessage = this.messagesContainer.firstElementChild;
                this.messagesContainer.innerHTML = '';
                this.messagesContainer.appendChild(welcomeMessage);
                this.showToast('Chat history cleared', 'success');
            } else {
                this.showToast(data.error || 'Failed to clear chat', 'error');
            }
        } catch (error) {
            console.error('Error clearing chat:', error);
            this.showToast('Failed to clear chat history', 'error');
        }
    }
    
    openSettings() {
        this.settingsModal.classList.add('show');
        this.userNameInput.focus();
    }
    
    closeSettings() {
        this.settingsModal.classList.remove('show');
    }
    
    saveSettings() {
        const userName = this.userNameInput.value.trim();
        const botName = this.botNameInput.value.trim();
        const customPrompt = this.customPromptInput.value.trim();
        
        if (!userName || !botName) {
            this.showToast('Name fields cannot be empty', 'error');
            return;
        }
        
        // Update configuration
        this.config.userName = userName;
        this.config.botName = botName;
        this.config.customPrompt = customPrompt;
        
        // Update UI
        this.botNameElement.textContent = botName;
        
        // Save to localStorage for persistence
        localStorage.setItem('chatConfig', JSON.stringify(this.config));
        
        this.closeSettings();
        this.showToast('Settings saved successfully', 'success');
    }
    
    resetSettings() {
        this.config = {
            botName: 'Assistant',
            userName: 'User',
            customPrompt: ''
        };
        
        this.updateUI();
        this.customPromptInput.value = '';
        localStorage.removeItem('chatConfig');
        this.showToast('Settings reset to default', 'success');
    }
    
    showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icon = document.createElement('div');
        icon.className = 'toast-icon';
        
        switch (type) {
            case 'success':
                icon.innerHTML = '<i class="fas fa-check-circle" style="color: #10b981;"></i>';
                break;
            case 'error':
                icon.innerHTML = '<i class="fas fa-exclamation-circle" style="color: #ef4444;"></i>';
                break;
            case 'warning':
                icon.innerHTML = '<i class="fas fa-exclamation-triangle" style="color: #f59e0b;"></i>';
                break;
        }
        
        const messageDiv = document.createElement('div');
        messageDiv.className = 'toast-message';
        messageDiv.textContent = message;
        
        toast.appendChild(icon);
        toast.appendChild(messageDiv);
        this.toastContainer.appendChild(toast);
        
        // Show toast
        setTimeout(() => toast.classList.add('show'), 100);
        
        // Hide and remove toast
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, 4000);
    }
    
    // Load saved configuration from localStorage
    loadSavedConfig() {
        try {
            const saved = localStorage.getItem('chatConfig');
            if (saved) {
                const config = JSON.parse(saved);
                this.config = { ...this.config, ...config };
                this.updateUI();
            }
        } catch (error) {
            console.error('Error loading saved config:', error);
        }
    }
}

// Initialize the chat interface when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const chatInterface = new ChatInterface();
    chatInterface.loadSavedConfig();
    
    // Focus on input after initialization
    setTimeout(() => {
        chatInterface.messageInput.focus();
    }, 100);
});