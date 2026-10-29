## 2024-06-22 - Form Accessibility & ARIA Labels in Settings
**Learning:** Found instances of `<label>` tags not associated with inputs (`htmlFor` / `id` missing), and an icon-only button without an `aria-label`.
**Action:** Always verify `htmlFor` matching `id` for labels, and ensure all icon-only interactive elements (like the eye icon for passwords) have descriptive `aria-label` or `title` attributes.
## 2024-11-20 - Redundant Screen Reader Output on Decorative SVG Icons
**Learning:** Purely decorative or redundant SVG icons (e.g., from `lucide-react`) within interactive elements that already have descriptive labels or text (like `aria-label="Save Edit"`) must be explicitly hidden from screen readers. Otherwise, screen readers may announce unnecessary technical SVG details or read 'image' redundantly.
**Action:** Always add `aria-hidden="true"` to `lucide-react` icons that are purely visual or accompany descriptive text/aria-labels.
## 2024-12-11 - Accessible Dynamic Search/Filter Empty States
**Learning:** For client-side dynamic search or filtering in the frontend, standard rendering of empty state messages (e.g., "No hosts match your search") are not announced by screen readers automatically since the DOM change happens dynamically without a page reload. Adding `aria-live="polite"` to a conditionally rendered element is generally ineffective because screen readers may miss the announcement when the node is injected into the DOM.
**Action:** Always add an always-mounted, visually hidden (`sr-only`) `aria-live="polite"` region whose text updates dynamically based on the list length/filter outcome, independent of the conditionally rendered visual empty state.
