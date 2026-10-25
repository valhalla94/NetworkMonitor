## 2024-11-20 - Redundant Screen Reader Output on Decorative SVG Icons
**Learning:** Purely decorative or redundant SVG icons (e.g., from `lucide-react`) within interactive elements that already have descriptive labels or text (like `aria-label="Save Edit"`) must be explicitly hidden from screen readers. Otherwise, screen readers may announce unnecessary technical SVG details or read "image" redundantly.
**Action:** Always add `aria-hidden="true"` to `lucide-react` icons that are purely visual or accompany descriptive text/aria-labels.
## 2026-10-25 - Live Region for Dynamic Filtering Results
**Learning:** When building client-side dynamic search or filtering features, screen readers will not announce updates unless an `aria-live` region is used. Conditionally mounting an `aria-live` region can cause screen readers to miss the first announcement.
**Action:** Always include a permanently mounted, visually hidden (`className="sr-only"`) `aria-live="polite"` container that dynamically updates its text content with the filter results count.
