## 2024-06-22 - Form Accessibility & ARIA Labels in Settings
**Learning:** Found instances of `<label>` tags not associated with inputs (`htmlFor` / `id` missing), and an icon-only button without an `aria-label`.
**Action:** Always verify `htmlFor` matching `id` for labels, and ensure all icon-only interactive elements (like the eye icon for passwords) have descriptive `aria-label` or `title` attributes.
## 2024-11-20 - Redundant Screen Reader Output on Decorative SVG Icons
**Learning:** Purely decorative or redundant SVG icons (e.g., from `lucide-react`) within interactive elements that already have descriptive labels or text (like `aria-label="Save Edit"`) must be explicitly hidden from screen readers. Otherwise, screen readers may announce unnecessary technical SVG details or read 'image' redundantly.
**Action:** Always add `aria-hidden="true"` to `lucide-react` icons that are purely visual or accompany descriptive text/aria-labels.
## 2024-11-20 - Adding explicit type="button" and aria-live polite regions
**Learning:** Found instances of `<button>` elements inside interactive components lacking `type="button"`, posing a risk of implicit form submission if wrapped inside a form later. Also, dynamic list filtering operations (like searching for hosts) lacked auditory feedback for screen reader users.
**Action:** Always add explicit `type="button"` to non-submitting buttons. Add a visually hidden `aria-live="polite"` region near search inputs to announce filtered result counts.
