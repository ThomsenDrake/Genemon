# Claude Code Loop Prompt

Analyze the current workspace and perform one of the following tasks:

1. **Fix bugs**: Look for errors, exceptions, or logical issues in the code
2. **Add tests**: Write unit tests for untested functions or modules
3. **Improve documentation**: Add helpful comments, docstrings, or README sections
4. **Refactor code**: Improve code quality, readability, or structure
5. **Optimize performance**: Find and fix performance bottlenecks
6. **Update dependencies**: Check for outdated packages and suggest updates
7. **Enhance security**: Identify and fix security vulnerabilities

## Guidelines

- Make **small, incremental improvements** in each iteration
- Focus on **one type of improvement** per iteration
- **Preserve existing functionality** - don't break working code
- **Document your changes** - explain what you did and why
- **Test your changes** when possible

## What to prioritize

1. Critical bugs or security issues (highest priority)
2. Missing tests for critical functions
3. Confusing or undocumented code
4. Code smells or anti-patterns
5. Minor improvements and polish

After each iteration, your changes will persist for the next iteration, allowing you to build on previous work.
