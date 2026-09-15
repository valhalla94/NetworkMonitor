## 2024-06-22 - Form Accessibility & ARIA Labels in Settings
**Learning:** Found instances of `<label>` tags not associated with inputs (`htmlFor` / `id` missing), and an icon-only button without an `aria-label`.
**Action:** Always verify `htmlFor` matching `id` for labels, and ensure all icon-only interactive elements (like the eye icon for passwords) have descriptive `aria-label` or `title` attributes.
## 2024-11-20 - Redundant Screen Reader Output on Decorative SVG Icons
**Learning:** Purely decorative or redundant SVG icons (e.g., from `lucide-react`) within interactive elements that already have descriptive labels or text (like `aria-label="Save Edit"`) must be explicitly hidden from screen readers. Otherwise, screen readers may announce unnecessary technical SVG details or read 'image' redundantly.
**Action:** Always add `aria-hidden="true"` to `lucide-react` icons that are purely visual or accompany descriptive text/aria-labels.
## 2024-11-21 - Focus Management for Dynamic Clear Buttons
**Learning:** When building search inputs with an associated "Clear" button that unmounts itself when the search query is emptied, focus can be lost and returned to the body (the default). This is confusing for keyboard users who expect to remain near the search area.
**Action:** Always use `useRef` to retain a reference to the input and explicitly call `.focus()` on it inside the `onClick` handler of the button just before state changes unmount the button.
