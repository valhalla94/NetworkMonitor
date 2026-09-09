## 2024-06-22 - Form Accessibility & ARIA Labels in Settings
**Learning:** Found instances of `<label>` tags not associated with inputs (`htmlFor` / `id` missing), and an icon-only button without an `aria-label`.
**Action:** Always verify `htmlFor` matching `id` for labels, and ensure all icon-only interactive elements (like the eye icon for passwords) have descriptive `aria-label` or `title` attributes.
## 2024-11-20 - Redundant Screen Reader Output on Decorative SVG Icons
**Learning:** Purely decorative or redundant SVG icons (e.g., from `lucide-react`) within interactive elements that already have descriptive labels or text (like `aria-label="Save Edit"`) must be explicitly hidden from screen readers. Otherwise, screen readers may announce unnecessary technical SVG details or read 'image' redundantly.
**Action:** Always add `aria-hidden="true"` to `lucide-react` icons that are purely visual or accompany descriptive text/aria-labels.
## 2024-05-19 - Returning Keyboard Focus on Unmounting Elements
**Learning:** When building accessible React UI components where clicking a button unmounts the button itself (e.g., a "Clear search" or "Clear filters" button that disappears when state clears), keyboard focus is lost and resets to the document body. This creates a confusing experience for screen reader and keyboard-only users.
**Action:** Always use a `useRef` to explicitly return keyboard focus to the associated input element (or another logical nearby element) when a button click causes its own unmounting.
