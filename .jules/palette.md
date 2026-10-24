## 2024-06-22 - Form Accessibility & ARIA Labels in Settings
**Learning:** Found instances of `<label>` tags not associated with inputs (`htmlFor` / `id` missing), and an icon-only button without an `aria-label`.
**Action:** Always verify `htmlFor` matching `id` for labels, and ensure all icon-only interactive elements (like the eye icon for passwords) have descriptive `aria-label` or `title` attributes.
## 2024-11-20 - Redundant Screen Reader Output on Decorative SVG Icons
**Learning:** Purely decorative or redundant SVG icons (e.g., from `lucide-react`) within interactive elements that already have descriptive labels or text (like `aria-label="Save Edit"`) must be explicitly hidden from screen readers. Otherwise, screen readers may announce unnecessary technical SVG details or read 'image' redundantly.
**Action:** Always add `aria-hidden="true"` to `lucide-react` icons that are purely visual or accompany descriptive text/aria-labels.

## 2026-10-24 - Explicit type attribute for interactive buttons
**Learning:** Interactive `<button>` elements in React applications default to `type="submit"`, which can cause unintended form submissions and page reloads if they are ever wrapped in a `<form>` context. This is a common accessibility and UX pitfall.
**Action:** Always explicitly set `type="button"` on all `<button>` elements used for UI interactions (e.g., toggles, clear actions, modal triggers) that are not meant to submit a form.
