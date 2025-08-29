# Pull Request

## 📝 Description
<!-- Provide a brief, clear description of what this PR does -->

## 🔧 Type of Change
- [ ] 🐛 Bug fix (non-breaking change which fixes an issue)
- [ ] ✨ New feature (non-breaking change which adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] 📚 Documentation update
- [ ] 🔧 Maintenance/refactoring (code improvements without functional changes)
- [ ] 🧪 Test improvements

## 🧪 Testing

### Test Coverage
- [ ] I have added tests that cover my changes
- [ ] All existing tests pass locally
- [ ] I have tested with multiple Django versions (if applicable)
- [ ] I have tested with different Python versions (if applicable)

### Manual Testing
<!-- Describe any manual testing you performed -->

## 📋 Django-Specific Checklist
- [ ] If this adds database migrations, they are backwards compatible
- [ ] If this modifies models, appropriate migrations are included
- [ ] If this adds new dependencies, they are added to `pyproject.toml`
- [ ] If this affects the admin interface, I have tested it
- [ ] If this changes the API, documentation is updated

## ✅ Code Quality Checklist
- [ ] My code follows the project's style guidelines (passes pre-commit hooks)
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings or errors
- [ ] I have checked for and removed any debugging code

## 🔗 Related Issues
<!-- Link to related issues using "Fixes #123", "Closes #123", or "Addresses #123" -->

## 📸 Screenshots (if applicable)
<!-- Add screenshots for UI changes or new features -->

## ⚠️ Breaking Changes
<!-- If this is a breaking change, describe what users need to do to migrate -->

## 📚 Documentation
- [ ] Code changes are reflected in docstrings
- [ ] README.md is updated if needed
- [ ] CHANGELOG.md entry added (if significant change)

## 🔍 Review Notes
<!-- Any specific areas you'd like reviewers to focus on -->

## 📦 Deployment Notes
<!-- Any special considerations for deployment -->

---
**Reviewer Guidelines:**
- Check that tests adequately cover the changes
- Verify Django compatibility across supported versions
- Ensure no breaking changes without proper deprecation
- Validate that migrations are safe and backwards compatible
