## 2024-06-22 - Form Accessibility & ARIA Labels in Settings
**Learning:** Found instances of `<label>` tags not associated with inputs (`htmlFor` / `id` missing), and an icon-only button without an `aria-label`.
**Action:** Always verify `htmlFor` matching `id` for labels, and ensure all icon-only interactive elements (like the eye icon for passwords) have descriptive `aria-label` or `title` attributes.
## 2024-11-20 - Redundant Screen Reader Output on Decorative SVG Icons
**Learning:** Purely decorative or redundant SVG icons (e.g., from `lucide-react`) within interactive elements that already have descriptive labels or text (like `aria-label="Save Edit"`) must be explicitly hidden from screen readers. Otherwise, screen readers may announce unnecessary technical SVG details or read 'image' redundantly.
**Action:** Always add `aria-hidden="true"` to `lucide-react` icons that are purely visual or accompany descriptive text/aria-labels.

## 2024-10-24 - Segmented Controls vs Single Toggle Buttons
**Learning:** Using a single button that flips its label (e.g. "{showUptimeChart ? 'Latency' : 'Uptime'}") is a severe UX anti-pattern for view switching because it's ambiguous whether the label indicates the *current* state or the *action* to reach the other state.
**Action:** Always replace these with clear, multi-button segmented controls using `<div role="group">` where each option is explicitly visible, and use `aria-pressed={true/false}` on the individual buttons to clearly communicate the active state to screen readers.
