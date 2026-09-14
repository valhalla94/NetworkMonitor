## 2024-06-22 - Form Accessibility & ARIA Labels in Settings
**Learning:** Found instances of `<label>` tags not associated with inputs (`htmlFor` / `id` missing), and an icon-only button without an `aria-label`.
**Action:** Always verify `htmlFor` matching `id` for labels, and ensure all icon-only interactive elements (like the eye icon for passwords) have descriptive `aria-label` or `title` attributes.
## 2024-11-20 - Redundant Screen Reader Output on Decorative SVG Icons
**Learning:** Purely decorative or redundant SVG icons (e.g., from `lucide-react`) within interactive elements that already have descriptive labels or text (like `aria-label="Save Edit"`) must be explicitly hidden from screen readers. Otherwise, screen readers may announce unnecessary technical SVG details or read 'image' redundantly.
**Action:** Always add `aria-hidden="true"` to `lucide-react` icons that are purely visual or accompany descriptive text/aria-labels.
## 2024-05-24 - Implement Search Keyboard Shortcut
**Learning:** For dashboard applications with many lists, users expect keyboard shortcuts (like '/') to quickly focus on the main search input without needing to use the mouse. Adding a visual `<kbd>` hint dramatically improves discoverability.
**Action:** When working on complex data-heavy dashboard views, consider adding a global keyboard listener for common actions like search (`/` or `Cmd+K`) and ensure there is an accessible visual affordance for the shortcut. Also, ensure pressing `Escape` clears and blurs the input for quick navigation resets.
