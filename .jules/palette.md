## 2024-06-22 - Form Accessibility & ARIA Labels in Settings
**Learning:** Found instances of `<label>` tags not associated with inputs (`htmlFor` / `id` missing), and an icon-only button without an `aria-label`.
**Action:** Always verify `htmlFor` matching `id` for labels, and ensure all icon-only interactive elements (like the eye icon for passwords) have descriptive `aria-label` or `title` attributes.
## 2024-11-20 - Redundant Screen Reader Output on Decorative SVG Icons
**Learning:** Purely decorative or redundant SVG icons (e.g., from `lucide-react`) within interactive elements that already have descriptive labels or text (like `aria-label="Save Edit"`) must be explicitly hidden from screen readers. Otherwise, screen readers may announce unnecessary technical SVG details or read 'image' redundantly.
**Action:** Always add `aria-hidden="true"` to `lucide-react` icons that are purely visual or accompany descriptive text/aria-labels.
## 2024-11-21 - Focus Management on Ephemeral UI Controls
**Learning:** Found instances where dynamically rendered or conditional UI controls (like 'Clear Search' or 'Reset Filters' buttons) remove themselves from the DOM onClick, causing keyboard focus to be completely lost and dropped back to the document body (`<body>`). This creates a very frustrating experience for keyboard and screen reader users who lose context.
**Action:** Always capture a `useRef` to a related persistent interactive element (e.g., the search input being cleared) and explicitly restore focus to it (`searchInputRef.current?.focus()`) within the same `onClick` handler right after clearing the state.
