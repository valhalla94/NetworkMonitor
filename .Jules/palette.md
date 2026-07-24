## 2024-06-22 - Form Accessibility & ARIA Labels in Settings
**Learning:** Found instances of `<label>` tags not associated with inputs (`htmlFor` / `id` missing), and an icon-only button without an `aria-label`.
**Action:** Always verify `htmlFor` matching `id` for labels, and ensure all icon-only interactive elements (like the eye icon for passwords) have descriptive `aria-label` or `title` attributes.

## 2024-07-24 - Toggle Button Accessibility
**Learning:** Found several toggle buttons (status filters, chart type, time ranges) that functioned as radio/toggle buttons visually but lacked semantic `aria-pressed` state and visible focus indicators for keyboard navigation.
**Action:** Always ensure custom toggle buttons use `aria-pressed={boolean}` and include `focus-visible:ring-2` to support both screen readers and keyboard users effectively.
