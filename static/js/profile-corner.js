/**
 * Profile Corner Display System
 * Shows current child's profile picture with dropdown to switch between family members
 */

class ProfileCornerManager {
    constructor() {
        this.currentChild = null;
        this.familyChildren = [];
        this.isDropdownOpen = false;
        this.profileContainer = null;
        
        this.init();
    }
    
    init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.initializeProfileCorner());
        } else {
            this.initializeProfileCorner();
        }
    }
    
    async initializeProfileCorner() {
        // Don't show profile corner on authentication pages
        const currentPath = window.location.pathname;
        const authPages = ['/parent-login', '/parent-signup', '/login', '/signup'];
        
        if (authPages.includes(currentPath)) {
            return; // Don't create profile corner on auth pages
        }
        
        this.createProfileCorner();
        await this.loadFamilyData();
        this.setupEventListeners();
    }
    
    createProfileCorner() {
        // Create profile corner container
        const profileCorner = document.createElement('div');
        profileCorner.id = 'profile-corner';
        profileCorner.className = 'profile-corner';
        
        profileCorner.innerHTML = `
            <div class="profile-picture" id="profile-picture">
                <i class="fas fa-user"></i>
            </div>
            
            <div class="profile-dropdown" id="profile-dropdown">
                <button class="dropdown-close" onclick="ProfileCorner.closeDropdown()">
                    <i class="fas fa-times"></i>
                </button>
                
                <div class="current-child-info" id="current-child-info">
                    <div class="current-child-name">Loading...</div>
                    <div class="current-child-age">Age: --</div>
                </div>
                
                <div class="switch-profile-section">
                    <span class="switch-profile-label">Switch to:</span>
                    <div class="children-list" id="children-list">
                        <!-- Children options will be populated here -->
                    </div>
                </div>
                
                <div class="profile-actions">
                    <a href="/profile" class="profile-action-btn btn-primary-action">
                        <i class="fas fa-cog"></i> Settings
                    </a>
                    <a href="/family-dashboard" class="profile-action-btn btn-secondary-action">
                        <i class="fas fa-home"></i> Family
                    </a>
                </div>
            </div>
        `;
        
        document.body.appendChild(profileCorner);
        this.profileContainer = profileCorner;
    }
    
    async loadFamilyData() {
        try {
            // Load current child data
            const currentChildData = await this.getCurrentChild();
            
            // Load family children list
            const familyData = await this.getFamilyChildren();
            
            this.currentChild = currentChildData;
            this.familyChildren = familyData;
            
            this.updateProfileDisplay();
            
        } catch (error) {
            console.log('Loading demo family data');
            this.loadDemoData();
        }
    }
    
    async getCurrentChild() {
        // Try to get current child from session storage first
        const storedChild = sessionStorage.getItem('currentChild');
        if (storedChild) {
            return JSON.parse(storedChild);
        }
        
        // Try to fetch from server
        const response = await fetch('/api/current-child');
        if (response.ok) {
            const data = await response.json();
            return data.child;
        }
        
        throw new Error('No current child found');
    }
    
    async getFamilyChildren() {
        const response = await fetch('/api/family-children');
        if (response.ok) {
            const data = await response.json();
            return data.children;
        }
        
        throw new Error('No family data found');
    }
    
    loadDemoData() {
        // Default guest user data
        this.familyChildren = [
            {
                id: 'guest_user',
                name: 'Guest',
                age: 7,
                grade: 'P2',
                profile_picture: null,
                is_current: true
            }
        ];
        
        this.currentChild = this.familyChildren[0];
        this.updateProfileDisplay();
    }
    
    updateProfileDisplay() {
        if (!this.currentChild || !this.profileContainer) return;
        
        // Update profile picture
        const profilePicture = document.getElementById('profile-picture');
        if (profilePicture) {
            if (this.currentChild.profile_picture) {
                profilePicture.innerHTML = `
                    <img src="/static/images/profile-pics/${this.currentChild.profile_picture}" 
                         alt="${this.currentChild.name}'s Profile"
                         onerror="this.style.display='none'; this.parentElement.innerHTML='<i class=\\"fas fa-user\\"></i>';">
                `;
            } else {
                // Use initials as fallback
                const initials = this.currentChild.name.split(' ').map(n => n[0]).join('').toUpperCase();
                profilePicture.innerHTML = initials;
                profilePicture.className = `profile-picture child-avatar-color-${(this.currentChild.id.charCodeAt(0) % 6) + 1}`;
            }
        }
        
        // Update current child info
        const currentChildInfo = document.getElementById('current-child-info');
        if (currentChildInfo) {
            currentChildInfo.innerHTML = `
                <div class="current-child-name">${this.currentChild.name}</div>
                <div class="current-child-age">Age: ${this.currentChild.age} | ${this.currentChild.grade || 'P' + Math.max(1, this.currentChild.age - 4)}</div>
            `;
        }
        
        // Update children list for switching
        this.updateChildrenList();
    }
    
    updateChildrenList() {
        const childrenList = document.getElementById('children-list');
        if (!childrenList || !this.familyChildren.length) return;
        
        childrenList.innerHTML = '';
        
        this.familyChildren.forEach(child => {
            const childOption = document.createElement('div');
            childOption.className = `child-option ${child.id === this.currentChild.id ? 'current' : ''}`;
            childOption.dataset.childId = child.id;
            
            let pictureContent;
            if (child.profile_picture) {
                pictureContent = `
                    <img src="/static/images/profile-pics/${child.profile_picture}" 
                         alt="${child.name}'s Profile"
                         onerror="this.style.display='none'; this.parentElement.innerHTML='${child.name.split(' ').map(n => n[0]).join('').toUpperCase()}';">
                `;
            } else {
                pictureContent = child.name.split(' ').map(n => n[0]).join('').toUpperCase();
            }
            
            childOption.innerHTML = `
                <div class="child-option-picture child-avatar-color-${(child.id.charCodeAt(0) % 6) + 1}">
                    ${pictureContent}
                </div>
                <div class="child-option-info">
                    <div class="child-option-name">${child.name}</div>
                    <div class="child-option-age">Age ${child.age} | ${child.grade || 'P' + Math.max(1, child.age - 4)}</div>
                </div>
            `;
            
            // Add click handler if not current child
            if (child.id !== this.currentChild.id) {
                childOption.addEventListener('click', () => this.switchToChild(child));
            }
            
            childrenList.appendChild(childOption);
        });
    }
    
    async switchToChild(child) {
        if (!child || child.id === this.currentChild.id) return;
        
        try {
            // Add switching animation
            this.profileContainer.classList.add('profile-switching');
            
            // Try to switch on server
            const response = await fetch('/api/switch-child-profile', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ child_id: child.id })
            });
            
            if (response.ok) {
                // Update session storage
                sessionStorage.setItem('currentChild', JSON.stringify(child));
                
                // Update current child
                this.currentChild = child;
                
                // Update family children current status
                this.familyChildren.forEach(c => {
                    c.is_current = c.id === child.id;
                });
                
                // Update display
                this.updateProfileDisplay();
                
                // Close dropdown
                this.closeDropdown();
                
                // Refresh page to update context
                setTimeout(() => {
                    window.location.reload();
                }, 500);
                
            } else {
                throw new Error('Failed to switch child on server');
            }
            
        } catch (error) {
            console.log('Switching child locally');
            
            // Local switch for demo
            this.currentChild = child;
            this.familyChildren.forEach(c => {
                c.is_current = c.id === child.id;
            });
            
            sessionStorage.setItem('currentChild', JSON.stringify(child));
            this.updateProfileDisplay();
            this.closeDropdown();
        } finally {
            // Remove switching animation
            setTimeout(() => {
                this.profileContainer.classList.remove('profile-switching');
            }, 500);
        }
    }
    
    setupEventListeners() {
        if (!this.profileContainer) return;
        
        // Profile corner click to toggle dropdown
        const profilePicture = document.getElementById('profile-picture');
        if (profilePicture) {
            profilePicture.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleDropdown();
            });
        }
        
        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!this.profileContainer.contains(e.target)) {
                this.closeDropdown();
            }
        });
        
        // Prevent dropdown clicks from closing it
        const dropdown = document.getElementById('profile-dropdown');
        if (dropdown) {
            dropdown.addEventListener('click', (e) => {
                e.stopPropagation();
            });
        }
        
        // ESC key to close dropdown
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeDropdown();
            }
        });
    }
    
    toggleDropdown() {
        if (this.isDropdownOpen) {
            this.closeDropdown();
        } else {
            this.openDropdown();
        }
    }
    
    openDropdown() {
        const dropdown = document.getElementById('profile-dropdown');
        if (dropdown) {
            dropdown.classList.add('show');
            this.isDropdownOpen = true;
            this.profileContainer.classList.add('active');
        }
    }
    
    closeDropdown() {
        const dropdown = document.getElementById('profile-dropdown');
        if (dropdown) {
            dropdown.classList.remove('show');
            this.isDropdownOpen = false;
            this.profileContainer.classList.remove('active');
        }
    }
    
    // Public methods for external access
    getCurrentChildData() {
        return this.currentChild;
    }
    
    getFamilyData() {
        return this.familyChildren;
    }
    
    refreshProfile() {
        this.loadFamilyData();
    }
}

// Global instance
let ProfileCorner;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    ProfileCorner = new ProfileCornerManager();
    
    // Make it globally accessible
    window.ProfileCorner = ProfileCorner;
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ProfileCornerManager;
}