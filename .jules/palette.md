## 2024-06-22 - Form Accessibility & ARIA Labels in Settings
**Learning:** Found instances of `<label>` tags not associated with inputs (`htmlFor` / `id` missing), and an icon-only button without an `aria-label`.
**Action:** Always verify `htmlFor` matching `id` for labels, and ensure all icon-only interactive elements (like the eye icon for passwords) have descriptive `aria-label` or `title` attributes.
## 2024-11-20 - Redundant Screen Reader Output on Decorative SVG Icons
**Learning:** Purely decorative or redundant SVG icons (e.g., from `lucide-react`) within interactive elements that already have descriptive labels or text (like `aria-label="Save Edit"`) must be explicitly hidden from screen readers. Otherwise, screen readers may announce unnecessary technical SVG details or read 'image' redundantly.
**Action:** Always add `aria-hidden="true"` to `lucide-react` icons that are purely visual or accompany descriptive text/aria-labels.
## 2024-11-20 - Announcing Dynamic Search Results
**Learning:** For client-side dynamic search or filtering in the frontend, ensure screen readers reliably announce the outcome by keeping an `aria-live="polite"` container permanently mounted in the DOM (e.g., using a visually hidden `.sr-only` wrapper) and updating its text content dynamically, rather than conditionally mounting/unmounting the `aria-live` region itself.
**Action:** Always ensure a visually hidden `aria-live` region is permanently rendered and dynamically populated with text (e.g. `${results.length} found`) for search/filter inputs.
