## 2024-06-22 - Form Accessibility & ARIA Labels in Settings
**Learning:** Found instances of `<label>` tags not associated with inputs (`htmlFor` / `id` missing), and an icon-only button without an `aria-label`.
**Action:** Always verify `htmlFor` matching `id` for labels, and ensure all icon-only interactive elements (like the eye icon for passwords) have descriptive `aria-label` or `title` attributes.
## 2024-11-20 - Redundant Screen Reader Output on Decorative SVG Icons
**Learning:** Purely decorative or redundant SVG icons (e.g., from `lucide-react`) within interactive elements that already have descriptive labels or text (like `aria-label="Save Edit"`) must be explicitly hidden from screen readers. Otherwise, screen readers may announce unnecessary technical SVG details or read 'image' redundantly.
**Action:** Always add `aria-hidden="true"` to `lucide-react` icons that are purely visual or accompany descriptive text/aria-labels.
## 2024-11-20 - Screen Reader Announcements for Dynamic Filtering
**Learning:** Conditionally mounting/unmounting an `aria-live` region during client-side search/filtering causes screen readers to miss the outcome announcement because the element wasn't in the accessibility tree.
**Action:** Ensure screen readers reliably announce outcomes by keeping an `aria-live="polite"` container permanently mounted in the DOM (using a `.sr-only` wrapper) and updating its text content dynamically.
