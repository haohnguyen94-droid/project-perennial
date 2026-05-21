# `frontend/src/hooks/` — TODO

Custom React hooks. API calls live here.

**Owner:** `@jaden`

---

## Data hooks (one per backend resource)

### Auth
- [ ] `useAuth()` — current user, login, logout, signup
- [ ] `useRequireAuth()` — redirect to login if not authed
- [ ] `useChangePassword()`

### Onboarding
- [ ] `useOnboarding()` — save interests, complete onboarding

### Homepage
- [ ] `useHomepage()` — the bundle endpoint (Affordable & Growing + Popular & Stable + Insight)
- [ ] `useAffordableGrowing()` — paginated list
- [ ] `usePopularStable()` — paginated list
- [ ] `useSearch(query)` — Homepage Search Bar autocomplete

### Events / Insight
- [ ] `useEvents()` — list events
- [ ] `useEvent(id)` — single event with all sections
- [ ] `useEventSources(eventId)` — News / Social Media / Analyst tabs

### Company Detail
- [ ] `useCompany(id)` — full company detail bundle
- [ ] `useCompanySentimentPulse(id, source)` — per-tab data
- [ ] `useWhyThisCompany(id)` — Key Reasons + Finance

### Watchlist
- [ ] `useWatchlist(filter)` — list with All / Companies / Sectors filter
- [ ] `useAddToWatchlist()` — mutation (single company OR sector OR bulk-add from event)
- [ ] `useRemoveFromWatchlist()` — mutation

### Settings / Profile
- [ ] `useUserProfile()` — get/update profile
- [ ] `useNotificationPreferences()` — get/update notifications
- [ ] `useUpdateInterests()`

---

## Utility hooks
- [ ] `useDebounce(value, delay)` — for search input
- [ ] `useToast()` — show success/error
- [ ] `useLocalStorage(key, default)` — non-sensitive prefs only

---

## REMOVED from earlier plan

- ❌ `useWeeklyDigest()`
- ❌ `useLearningTerm()`
- ❌ `useMarketHealth()`

---

## Convention

- [ ] Use React Query (or SWR) for all data fetching
- [ ] Return `{ data, isLoading, error }` consistently
- [ ] Centralize API base URL in `../utils/api.ts`
- [ ] Type every hook's return value
