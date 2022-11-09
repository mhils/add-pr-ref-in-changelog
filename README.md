# add-pr-ref-in-changelog

This GitHub Action adds pull request references to changelog entries.

To be used with [<img alt="autofix logo" src="https://autofix.ci/logo/logo.png" width=16> autofix.ci](https://autofix.ci).

**Before:**
```markdown
# Release History

## Unreleased: example_tool next

 - Add feature
```

**After:**
```markdown
# Release History

## Unreleased: example_tool next

 - Add feature
   ([#42](https://github.com/mhils/add-pr-ref-in-changelog/pulls/42), @mhils)
```
