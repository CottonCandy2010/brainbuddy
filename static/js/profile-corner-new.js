/**
 * Profile Corner Display System - Rewritten for Better Compatibility
 * Shows current child's profile picture with dropdown to switch between family members
 */

(function() {
    'use strict';
    
    // Check if we're on an authentication page - don't load profile corner
    const authPages = ['/parent-login', '/parent-signup', '/login', '/signup'];
    const currentPath = window.location.pathname;
    
    if (authPages.includes(currentPath)) {
        console.log('Authentication page detected, skipping profile corner');
        return;
    }
    
    class ProfileCorner {
        constructor() {
            this.currentChild = null;
            this.familyChildren = [];
            this.isDropdownOpen = false;
            this.profileContainer = null;
            
            // Wait for DOM to be ready
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => this.initialize());
            } else {
                this.initialize();
            }
        }
        
        async initialize() {
            try {
                await this.createProfileCorner();
                await this.loadFamilyData();
                this.setupEventListeners();
                console.log('Profile corner initialized successfully');
            } catch (error) {
                console.error('Error initializing profile corner:', error);
            }
        }
        
        async createProfileCorner() {
            // Remove any existing profile corner
            const existing = document.getElementById('profile-corner');
            if (existing) {
                existing.remove();
            }
            
            // Create new profile corner
            const profileCorner = document.createElement('div');
            profileCorner.id = 'profile-corner';
            profileCorner.className = 'profile-corner';
            profileCorner.style.cssText = `
                position: fixed;
                top: 15px;
                right: 25px;
                z-index: 10000;
                width: 45px;
                height: 45px;
                cursor: pointer;
                transition: all 0.3s ease;
            `;
            
            profileCorner.innerHTML = `
                <div class="profile-picture" style="
                    width: 45px;
                    height: 45px;
                    border-radius: 50%;
                    border: 2px solid #fff;
                    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.2);
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-size: 14px;
                    font-weight: bold;
                    transition: all 0.3s ease;
                ">
                    G
                </div>
                
                <div class="profile-dropdown" style="
                    position: absolute;
                    top: 55px;
                    right: 0;
                    background: white;
                    border-radius: 12px;
                    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
                    padding: 10px;
                    min-width: 180px;
                    opacity: 0;
                    visibility: hidden;
                    transform: translateY(-10px);
                    transition: all 0.3s ease;
                    z-index: 10001;
                ">
                    <button class="dropdown-close" style="
                        position: absolute;
                        top: 8px;
                        right: 8px;
                        background: none;
                        border: none;
                        color: #6c757d;
                        cursor: pointer;
                        padding: 4px;
                    ">
                        <i class="fas fa-times"></i>
                    </button>
                    
                    <div class="current-child-info" style="
                        text-align: center;
                        padding: 10px;
                        border-bottom: 2px solid #f8f9fa;
                        margin-bottom: 15px;
                    ">
                        <div class="current-child-name" style="
                            font-size: 14px;
                            font-weight: 700;
                            color: #495057;
                            margin-bottom: 5px;
                        ">Guest</div>
                        <div class="current-child-age" style="
                            font-size: 11px;
                            color: #6c757d;
                            background: #e7f3ff;
                            padding: 2px 6px;
                            border-radius: 12px;
                            display: inline-block;
                        ">Age: 7 | P2</div>
                    </div>
                    
                    <div class="switch-profile-section">
                        <h6 style="font-size: 12px; color: #6c757d; margin-bottom: 10px;">Switch Profile</h6>
                        <div class="family-children-list" id="family-children-list">
                            <!-- Family members will be loaded here -->
                        </div>
                    </div>
                </div>
            `;
            
            // Add to body
            document.body.appendChild(profileCorner);
            this.profileContainer = profileCorner;
        }
        
        async loadFamilyData() {
            try {
                console.log('Loading demo family data');
                
                // Demo data for Guest user
                this.currentChild = {
                    id: 'guest',
                    name: 'Guest',
                    age: 7,
                    grade: 'P2',
                    profile_picture: null,
                    selected_avatar: null
                };
                
                this.familyChildren = [this.currentChild];
                this.updateProfileDisplay();
                this.populateFamilyDropdown();
                
            } catch (error) {
                console.error('Error loading family data:', error);
                this.loadOfflineData();
            }
        }
        
        loadOfflineData() {
            this.currentChild = {
                id: 'guest',
                name: 'Guest',
                age: 7,
                grade: 'P2',
                profile_picture: null
            };
            this.familyChildren = [this.currentChild];
            this.updateProfileDisplay();
        }
        
        updateProfileDisplay() {
            if (!this.currentChild || !this.profileContainer) return;
            
            const profilePicture = this.profileContainer.querySelector('.profile-picture');
            const nameElement = this.profileContainer.querySelector('.current-child-name');
            const ageElement = this.profileContainer.querySelector('.current-child-age');
            
            if (profilePicture) {
                // Check for selected avatar first
                const selectedAvatar = this.getSelectedAvatar();
                console.log('Selected avatar path:', selectedAvatar);
                
                if (selectedAvatar) {
                    const img = document.createElement('img');
                    img.src = selectedAvatar;
                    img.alt = "Selected Avatar";
                    img.style.cssText = "width: 100%; height: 100%; border-radius: 50%; object-fit: cover;";
                    
                    // Handle image load error
                    img.onerror = () => {
                        console.log('Avatar image failed to load:', selectedAvatar);
                        profilePicture.textContent = this.currentChild.name.charAt(0).toUpperCase();
                    };
                    
                    img.onload = () => {
                        console.log('Avatar image loaded successfully:', selectedAvatar);
                    };
                    
                    profilePicture.innerHTML = '';
                    profilePicture.appendChild(img);
                } else if (this.currentChild.profile_picture) {
                    profilePicture.innerHTML = `<img src="${this.currentChild.profile_picture}" alt="${this.currentChild.name}" style="width: 100%; height: 100%; border-radius: 50%; object-fit: cover;">`;
                } else {
                    profilePicture.textContent = this.currentChild.name.charAt(0).toUpperCase();
                }
            }
            
            if (nameElement) {
                nameElement.textContent = this.currentChild.name;
            }
            
            if (ageElement) {
                ageElement.textContent = `Age: ${this.currentChild.age} | ${this.currentChild.grade}`;
            }
        }
        
        getSelectedAvatar() {
            // Check localStorage for selected avatar
            const selectedAvatar = localStorage.getItem('selectedAvatar');
            if (selectedAvatar && selectedAvatar !== 'null' && selectedAvatar !== 'undefined') {
                return `/static/images/profile-pics/${selectedAvatar}`;
            }
            
            // Check sessionStorage as backup
            const sessionAvatar = sessionStorage.getItem('selectedAvatar');
            if (sessionAvatar && sessionAvatar !== 'null' && sessionAvatar !== 'undefined') {
                return `/static/images/profile-pics/${sessionAvatar}`;
            }
            
            return null;
        }
        
        // Method to update avatar when selection changes
        updateAvatar(avatarFileName) {
            if (this.currentChild) {
                this.currentChild.selected_avatar = avatarFileName;
                localStorage.setItem('selectedAvatar', avatarFileName);
                this.updateProfileDisplay();
                console.log(`Profile avatar updated to: ${avatarFileName}`);
            }
        }
        
        populateFamilyDropdown() {
            if (!this.familyChildren || !this.profileContainer) return;
            
            const familyList = this.profileContainer.querySelector('#family-children-list');
            if (!familyList) return;
            
            familyList.innerHTML = '';
            
            this.familyChildren.forEach(child => {
                const childOption = document.createElement('div');
                childOption.className = 'child-option';
                childOption.style.cssText = `
                    display: flex;
                    align-items: center;
                    padding: 8px 10px;
                    border-radius: 8px;
                    cursor: pointer;
                    transition: all 0.2s ease;
                    margin-bottom: 5px;
                    ${child.id === this.currentChild.id ? 'background: #e7f3ff; border: 1px solid #4a90e2;' : ''}
                `;
                
                const initial = child.name.charAt(0).toUpperCase();
                childOption.innerHTML = `
                    <div style="
                        width: 32px;
                        height: 32px;
                        border-radius: 50%;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 12px;
                        font-weight: bold;
                        margin-right: 10px;
                    ">${initial}</div>
                    <div style="flex: 1;">
                        <div style="font-size: 13px; font-weight: 600; color: #495057;">${child.name}</div>
                        <div style="font-size: 11px; color: #6c757d;">Age ${child.age} | ${child.grade}</div>
                    </div>
                `;
                
                // Add click handler for switching
                if (child.id !== this.currentChild.id) {
                    childOption.addEventListener('click', () => this.switchToChild(child));
                    childOption.addEventListener('mouseenter', () => {
                        childOption.style.background = '#f8f9fa';
                        childOption.style.transform = 'translateX(3px)';
                    });
                    childOption.addEventListener('mouseleave', () => {
                        childOption.style.background = '';
                        childOption.style.transform = 'translateX(0)';
                    });
                }
                
                familyList.appendChild(childOption);
            });
        }
        
        switchToChild(child) {
            if (!child || child.id === this.currentChild.id) return;
            
            // Update current child
            this.currentChild = child;
            
            // Update display immediately to show letter change
            this.updateProfileDisplay();
            
            // Update dropdown options
            this.populateFamilyDropdown();
            
            // Close dropdown
            this.closeDropdown();
            
            console.log(`Switched to ${child.name} - Profile letter changed to ${child.name.charAt(0).toUpperCase()}`);
        }
        
        setupEventListeners() {
            if (!this.profileContainer) return;
            
            const profilePicture = this.profileContainer.querySelector('.profile-picture');
            const dropdown = this.profileContainer.querySelector('.profile-dropdown');
            const closeButton = this.profileContainer.querySelector('.dropdown-close');
            
            // Click to toggle dropdown
            if (profilePicture) {
                profilePicture.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.toggleDropdown();
                });
            }
            
            // Close button
            if (closeButton) {
                closeButton.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.closeDropdown();
                });
            }
            
            // Click outside to close
            document.addEventListener('click', (e) => {
                if (!this.profileContainer.contains(e.target)) {
                    this.closeDropdown();
                }
            });
            
            // Hover effects
            if (profilePicture) {
                profilePicture.addEventListener('mouseenter', () => {
                    profilePicture.style.transform = 'scale(1.05)';
                    profilePicture.style.boxShadow = '0 8px 25px rgba(0, 0, 0, 0.3)';
                });
                
                profilePicture.addEventListener('mouseleave', () => {
                    profilePicture.style.transform = 'scale(1)';
                    profilePicture.style.boxShadow = '0 4px 15px rgba(0, 0, 0, 0.2)';
                });
            }
        }
        
        toggleDropdown() {
            this.isDropdownOpen ? this.closeDropdown() : this.openDropdown();
        }
        
        openDropdown() {
            if (!this.profileContainer) return;
            
            const dropdown = this.profileContainer.querySelector('.profile-dropdown');
            if (dropdown) {
                dropdown.style.opacity = '1';
                dropdown.style.visibility = 'visible';
                dropdown.style.transform = 'translateY(0)';
                this.isDropdownOpen = true;
            }
        }
        
        closeDropdown() {
            if (!this.profileContainer) return;
            
            const dropdown = this.profileContainer.querySelector('.profile-dropdown');
            if (dropdown) {
                dropdown.style.opacity = '0';
                dropdown.style.visibility = 'hidden';
                dropdown.style.transform = 'translateY(-10px)';
                this.isDropdownOpen = false;
            }
        }
    }
    
    // Initialize profile corner
    window.ProfileCornerInstance = new ProfileCorner();
    
    // Global function to update profile avatar from avatar selection
    window.updateProfileAvatar = function(avatarFileName) {
        if (window.ProfileCornerInstance) {
            window.ProfileCornerInstance.updateAvatar(avatarFileName);
        }
    };
    
    // Listen for localStorage changes to update profile when avatar is selected
    window.addEventListener('storage', function(e) {
        if (e.key === 'selectedAvatar' && window.ProfileCornerInstance) {
            window.ProfileCornerInstance.updateProfileDisplay();
        }
    });
    
})();