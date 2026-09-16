## 2024-06-22 - Form Accessibility & ARIA Labels in Settings
**Learning:** Found instances of `<label>` tags not associated with inputs (`htmlFor` / `id` missing), and an icon-only button without an `aria-label`.
**Action:** Always verify `htmlFor` matching `id` for labels, and ensure all icon-only interactive elements (like the eye icon for passwords) have descriptive `aria-label` or `title` attributes.
## 2024-11-20 - Redundant Screen Reader Output on Decorative SVG Icons
**Learning:** Purely decorative or redundant SVG icons (e.g., from `lucide-react`) within interactive elements that already have descriptive labels or text (like `aria-label="Save Edit"`) must be explicitly hidden from screen readers. Otherwise, screen readers may announce unnecessary technical SVG details or read 'image' redundantly.
**Action:** Always add `aria-hidden="true"` to `lucide-react` icons that are purely visual or accompany descriptive text/aria-labels.
## 2024-11-22 - Focus Management on Ephemeral UI Elements
**Learning:** When interactive elements (like a "Clear Search" button) unmount themselves upon clicking, keyboard focus is lost and resets to the document body, severely disrupting keyboard and screen reader navigation.
**Action:** When a button action causes the button itself to disappear (like clearing an input), use a `useRef` to explicitly shift focus back to the logical next or previous element (e.g., the input field that was just cleared) to maintain a seamless keyboard navigation experience.
