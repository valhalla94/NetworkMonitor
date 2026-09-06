## 2024-06-22 - Form Accessibility & ARIA Labels in Settings
**Learning:** Found instances of `<label>` tags not associated with inputs (`htmlFor` / `id` missing), and an icon-only button without an `aria-label`.
**Action:** Always verify `htmlFor` matching `id` for labels, and ensure all icon-only interactive elements (like the eye icon for passwords) have descriptive `aria-label` or `title` attributes.
## 2024-11-20 - Redundant Screen Reader Output on Decorative SVG Icons
**Learning:** Purely decorative or redundant SVG icons (e.g., from `lucide-react`) within interactive elements that already have descriptive labels or text (like `aria-label="Save Edit"`) must be explicitly hidden from screen readers. Otherwise, screen readers may announce unnecessary technical SVG details or read 'image' redundantly.
**Action:** Always add `aria-hidden="true"` to `lucide-react` icons that are purely visual or accompany descriptive text/aria-labels.
## 2026-09-06 - Prevent Focus Loss on Search Clear
**Learning:** When building accessible React UI components where clicking a button unmounts the button itself (e.g., a 'Clear search' or 'Clear filters' button), focus is lost and resets to the document body, causing a confusing experience for keyboard users and screen readers.
**Action:** Use a `useRef` to explicitly return keyboard focus to the associated input element before or as the button unmounts to ensure a seamless accessibility experience.
