## 2024-06-22 - Form Accessibility & ARIA Labels in Settings
**Learning:** Found instances of `<label>` tags not associated with inputs (`htmlFor` / `id` missing), and an icon-only button without an `aria-label`.
**Action:** Always verify `htmlFor` matching `id` for labels, and ensure all icon-only interactive elements (like the eye icon for passwords) have descriptive `aria-label` or `title` attributes.
## 2024-11-20 - Redundant Screen Reader Output on Decorative SVG Icons
**Learning:** Purely decorative or redundant SVG icons (e.g., from `lucide-react`) within interactive elements that already have descriptive labels or text (like `aria-label="Save Edit"`) must be explicitly hidden from screen readers. Otherwise, screen readers may announce unnecessary technical SVG details or read 'image' redundantly.
**Action:** Always add `aria-hidden="true"` to `lucide-react` icons that are purely visual or accompany descriptive text/aria-labels.
## 2025-02-27 - Semantic ARIA Grouping for Toggle Buttons
**Learning:** Groups of toggle buttons (like time range selectors) benefit significantly from `role="group"` and `aria-label` attributes, which help screen readers announce the context of the buttons together.
**Action:** Always wrap related toggle button groups in a container with `role="group"` and a descriptive `aria-label`.
## 2025-02-27 - Dynamic Empty States Need aria-live
**Learning:** When client-side filtering results in an empty state (e.g., 'No hosts match'), screen readers may not announce this visual change automatically.
**Action:** Apply `aria-live="polite"` to containers rendering empty state messages after dynamic filtering.
