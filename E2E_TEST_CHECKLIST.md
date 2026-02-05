# End-to-End Testing Checklist

## Issue #50: E2E Verification

### Test Environment Setup
- [ ] Ensure backend is running (`http://localhost:8000`)
- [ ] Ensure frontend is running (`http://localhost:3000`)
- [ ] Ensure MongoDB is connected
- [ ] Clear browser localStorage and cookies

### Test Cases

#### 1. Fresh Start
- [ ] Clear localStorage (DevTools > Application > Local Storage > Clear)
- [ ] Navigate to `/evaluate`
- [ ] Verify "My Repos" tab shows login prompt

#### 2. GitHub OAuth Flow
- [ ] Click "Login with GitHub" button
- [ ] Complete GitHub OAuth authorization
- [ ] Verify redirect back to app with token
- [ ] Verify repositories load automatically

#### 3. Repository Selection
- [ ] Search for repository by name
- [ ] Select a repository from list
- [ ] Verify URL auto-fills in hidden field
- [ ] Click "Start Tasting"
- [ ] Verify evaluation starts and redirects to progress page

#### 4. Manual URL Input
- [ ] Switch to "Enter URL" tab
- [ ] Type valid GitHub URL
- [ ] Verify real-time validation shows green checkmark
- [ ] Click "Start Tasting"
- [ ] Verify evaluation starts

#### 5. Invalid URL Handling
- [ ] Enter invalid URL format
- [ ] Verify validation shows red X
- [ ] Verify error message displays

#### 6. Token Expiration
- [ ] Wait for token to expire (or manually clear)
- [ ] Try to refresh repositories
- [ ] Verify re-authentication modal appears
- [ ] Click "Login with GitHub" in modal
- [ ] Verify OAuth flow completes successfully

#### 7. Cache Functionality
- [ ] Load repositories (first time - from GitHub)
- [ ] Refresh page
- [ ] Verify repositories load from cache (faster)
- [ ] Click refresh button
- [ ] Verify fresh data loads from GitHub

#### 8. Private Repository Access
- [ ] Ensure GitHub token has `repo` scope
- [ ] Verify private repositories appear in list
- [ ] Select private repository
- [ ] Verify evaluation can start

### Screenshots Required
- [ ] Screenshot: Login prompt on My Repos tab
- [ ] Screenshot: Repository list after login
- [ ] Screenshot: Search filtering repositories
- [ ] Screenshot: Selected repository with auto-filled URL
- [ ] Screenshot: Successful evaluation redirect
- [ ] Screenshot: Re-authentication modal

### Browser Compatibility
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)

### Mobile Responsiveness
- [ ] Test on mobile viewport (375px width)
- [ ] Test on tablet viewport (768px width)
- [ ] Verify tabs are accessible
- [ ] Verify repository picker scrolls properly

## Test Results

**Date:** ___________
**Tester:** ___________
**Status:** ⬜ All Passed / ⬜ Some Issues Found

### Issues Found
<!-- Document any issues discovered during testing -->

1. 
2. 
3. 

### Notes
<!-- Any additional observations or comments -->
