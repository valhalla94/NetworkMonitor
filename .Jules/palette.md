## 2024-06-22 - Form Accessibility & ARIA Labels in Settings
**Learning:** Found instances of `<label>` tags not associated with inputs (`htmlFor` / `id` missing), and an icon-only button without an `aria-label`.
**Action:** Always verify `htmlFor` matching `id` for labels, and ensure all icon-only interactive elements (like the eye icon for passwords) have descriptive `aria-label` or `title` attributes.

## 2024-06-25 - Checkbox Focus Outlines & Tailwind Preflight
**Learning:** Tailwind's preflight CSS resets native focus outlines on interactive elements like `<input type="checkbox">`, making them invisible to keyboard navigation unless explicitly styled.
**Action:** When using standard form elements (especially native checkboxes and radios) in this codebase, explicitly apply `focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500` classes to preserve visible focus rings for keyboard users.
