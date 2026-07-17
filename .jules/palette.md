## 2025-02-12 - Icon Button Accessibility
**Learning:** Icon-only buttons for CRUD operations (like Edit, Delete, Save, Close) within tables or modals in the network monitor UI were missing `aria-label`s and visible keyboard focus states (`focus:outline-none focus-visible:ring-2`), making them inaccessible to screen readers and keyboard users.
**Action:** Always ensure any icon-only button uses an explicit `aria-label` and `focus-visible:ring-2` to provide proper feedback for all modes of interaction. When validating these in UI test scripts, be aware that getting past the Settings login gate requires accurate API mocking (e.g. `api/auth/verify`, `api/token`, and `api/hosts`).

## 2023-10-25 - Unique IDs for Reusable Form Components
**Learning:** Reusable form components like `HostFormFields.jsx` can cause accessibility and functional issues if static IDs are used, as rendering the component multiple times (e.g., in a main panel and an inline table edit row simultaneously) creates duplicate IDs. Duplicate IDs break the explicit `htmlFor` to `id` association for screen readers and label clicking.
**Action:** Always use React's `useId()` hook to generate a unique prefix for `id`s within reusable form components to ensure explicit label associations are safely maintained without risk of ID collisions.

## 2025-02-12 - Adding Loading State Feedback to Authentication Forms
**Learning:** Asynchronous authentication forms lacking visual loading feedback leave users confused about system state. Without disabled inputs and clear loading indicators (like changing "Unlock Settings" to a disabled "Unlocking..." state with a spinner), users might repeatedly click submit, leading to multiple API calls or a perceived frozen UI.
**Action:** Always add interactive loading states (disabled buttons, spinners, and progressing text) to authentication and critical action buttons, ensuring screen readers also receive appropriate `aria-disabled` or disabled attributes during the pending phase.
