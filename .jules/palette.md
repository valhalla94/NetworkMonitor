## 2024-06-22 - Form Accessibility & ARIA Labels in Settings
**Learning:** Found instances of `<label>` tags not associated with inputs (`htmlFor` / `id` missing), and an icon-only button without an `aria-label`.
**Action:** Always verify `htmlFor` matching `id` for labels, and ensure all icon-only interactive elements (like the eye icon for passwords) have descriptive `aria-label` or `title` attributes.
## 2024-11-20 - Redundant Screen Reader Output on Decorative SVG Icons
**Learning:** Purely decorative or redundant SVG icons (e.g., from `lucide-react`) within interactive elements that already have descriptive labels or text (like `aria-label="Save Edit"`) must be explicitly hidden from screen readers. Otherwise, screen readers may announce unnecessary technical SVG details or read 'image' redundantly.
**Action:** Always add `aria-hidden="true"` to `lucide-react` icons that are purely visual or accompany descriptive text/aria-labels.
## 2024-11-20 - Focus Management when Unmounting or Modifying Context
**Learning:** When users click a button to clear an input (like a search bar) or reset filters, and that action removes the button from the DOM or changes context, keyboard focus is often lost and resets to the document `<body>`.
**Action:** Use a `useRef` pointing to the primary input being modified (e.g., `searchInputRef`). When the "Clear" action is triggered, immediately call `ref.current?.focus()` after updating the state to keep the user exactly where they intend to be.
