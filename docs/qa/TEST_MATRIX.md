# Test Matrix

This file tracks required states and their current coverage. Testing policy lives in [TESTING.md](TESTING.md).

## Shared Shell States

| Matrix ID | Spec | State | Coverage mode | Current evidence | Status |
| --- | --- | --- | --- | --- | --- |
| `G-01` | `GLOBAL.md` | Base shell includes skip link, shared header, `main#main-content`, and shared footer. | View test | `tests/core/test_views.py::test_shared_shell_landmarks_present_on_primary_public_routes` | Covered |
| `G-02` | `GLOBAL.md` | Skip link targets `#main-content`. | View test | `tests/core/test_views.py::test_skip_link_targets_main_content` | Covered |
| `G-03` | `GLOBAL.md` | Metadata falls back to bundled OG image when no custom image exists. | View test | `tests/pages/test_views.py::test_home_page` | Covered |
| `G-04` | `GLOBAL.md` | Header gains `.scrolled` after scroll threshold. | Browser e2e | `tests/e2e/test_navigation.py::test_header_gains_and_loses_scrolled_state_on_scroll` | Covered |
| `G-05` | `GLOBAL.md` | Mobile menu open/close updates `aria-expanded` and body scroll lock. | Browser e2e | `tests/e2e/test_navigation.py::test_mobile_navigation_opens_closes_and_navigates` | Covered |
| `G-06` | `GLOBAL.md` | `Escape` closes the open mobile menu and restores focus. | Browser e2e | `tests/e2e/test_navigation.py::test_mobile_navigation_keyboard_focus_moves_into_menu_and_returns_on_escape` | Covered |
| `G-07` | `GLOBAL.md` | Crossing above the mobile breakpoint closes the menu and removes scroll lock. | Browser e2e | `tests/e2e/test_navigation.py::test_mobile_navigation_recovers_when_viewport_crosses_breakpoint` | Covered |
| `G-08` | `GLOBAL.md` | Shared focus-visible treatment remains present. | Browser e2e | `tests/e2e/test_navigation.py::test_keyboard_focus_uses_shared_focus_visible_outline` | Covered |
| `G-09` | `GLOBAL.md` | Shared reduced-motion rules prevent avoidable shell or hero motion where implemented. | Browser e2e | `tests/e2e/test_homepage.py::test_homepage_reduced_motion_disables_hero_animation_and_transition` | Covered |
| `G-10` | `GLOBAL.md` | No horizontal page overflow occurs at required baseline viewports. | No dedicated current assertion | No dedicated current evidence is tracked yet. This remains an explicit global evidence gap from the `2026-03-31` doc-to-implementation sync audit. | Gap |

## Release Readiness States

| Matrix ID | Spec | State | Coverage mode | Current evidence | Status |
| --- | --- | --- | --- | --- | --- |
| `R-01` | Current release implementation | Deterministic public smoke covers the privacy route in both the smoke script and shared public-route coverage. | View test + smoke script review | `tests/core/test_views.py::test_shared_shell_landmarks_present_on_primary_public_routes`; `scripts/smoke_check.py` route review (`2026-03-31`) | Covered |
| `R-02` | Current shared-template implementation | The GA script is omitted when `google_analytics_id` is blank and rendered with the configured measurement ID when it is set. | View test | `tests/core/test_views.py::test_base_template_omits_google_analytics_script_when_measurement_id_is_blank`; `tests/core/test_views.py::test_base_template_renders_google_analytics_script_when_measurement_id_is_set` | Covered |

## Typography States

| Matrix ID | Spec | State | Coverage mode | Current evidence | Status |
| --- | --- | --- | --- | --- | --- |
| `T-01` | `TYPOGRAPHY.md` | Base template loads both Google Fonts families once with `display=swap`. | Direct template review | `templates/base.html` font-loading review (`2026-03-30`) | Covered |
| `T-02` | `TYPOGRAPHY.md` | `body` remains `DM Sans`, `1rem`, `400`, `1.7`. | Direct CSS review | `static/css/base/base.css` body-rule review (`2026-03-30`) | Covered |
| `T-03` | `TYPOGRAPHY.md` | Desktop hero title, subtitle, and CTA hierarchy remain visibly ordered and readable. | Manual screenshot audit | March 2026 typography refinement review — desktop hero state | Covered |
| `T-04` | `TYPOGRAPHY.md` | Tablet hero subtitle retains real second-level hierarchy and does not collapse into generic body copy. | Manual screenshot audit | March 2026 typography refinement review — tablet hero state | Covered |
| `T-05` | `TYPOGRAPHY.md` | Mobile hero title remains readable over imagery with current weight and line-height rules. | Manual screenshot audit | March 2026 typography refinement review — mobile hero state | Covered |
| `T-06` | `TYPOGRAPHY.md` | Long hero title wraps without cramped leading or broken composition. | Manual screenshot audit | March 2026 typography refinement review — long-title mobile stress state | Covered |
| `T-07` | `TYPOGRAPHY.md` | Project card titles still read as titles at tablet and desktop widths. | Manual screenshot audit | March 2026 typography refinement review — project-card desktop and tablet states | Covered |
| `T-08` | `TYPOGRAPHY.md` | Body, footer, and supporting text remain readable after current body-weight and micro-scale rules. | Direct CSS review + manual screenshot audit | `static/css/base/base.css`; `static/css/components/footer.css`; March 2026 typography refinement review — body and footer readability | Covered |
| `T-09` | `TYPOGRAPHY.md` | Brand text, monogram, and mobile overlay links remain typographically distinct from desktop utility nav text. | Browser e2e + direct CSS review | `tests/e2e/test_navigation.py::test_contact_nav_cta_keeps_desktop_style_and_resets_in_mobile_overlay`; `static/css/components/nav.css` brand and overlay typography review (`2026-03-30`) | Covered |

## Layout States

| Matrix ID | Spec | State | Coverage mode | Current evidence | Status |
| --- | --- | --- | --- | --- | --- |
| `L-01` | `LAYOUT.md` | `.container` maxes at `1280px` and keeps gutter padding on both sides. | Direct CSS review | `static/css/base/tokens.css`; `static/css/base/base.css` container review (`2026-03-30`) | Covered |
| `L-02` | `LAYOUT.md` | `.container--narrow` maxes at `780px`. | Direct CSS review | `static/css/base/tokens.css`; `static/css/base/base.css` narrow-container review (`2026-03-30`) | Covered |
| `L-03` | `LAYOUT.md` | `.section` uses `7rem` vertical padding on desktop and `4rem` at `<=768px`. | Direct CSS review | `static/css/base/tokens.css`; `static/css/base/base.css` section-rhythm review (`2026-03-30`) | Covered |
| `L-04` | `LAYOUT.md` | Fixed header height and `.filter-bar` top offset both remain `4.5rem`. | Direct CSS review | `static/css/components/nav.css`; `apps/projects/static/css/project-cards.css` sticky-offset review (`2026-03-30`) | Covered |
| `L-05` | `LAYOUT.md` | Homepage grid HTML includes `hp-mob-N` and `hp-tab-N` classes that match current `SiteSettings`. | View test | `tests/pages/test_views.py::test_homepage_grid_has_breakpoint_count_classes` | Covered |
| `L-06` | `LAYOUT.md` | Invalid homepage count combinations fail model validation before they reach templates. | Model tests | `tests/core/test_models.py::test_site_settings_homepage_project_count_rejects_out_of_range`; `tests/core/test_models.py::test_site_settings_homepage_project_count_rejects_mobile_greater_than_tablet`; `tests/core/test_models.py::test_site_settings_homepage_project_count_rejects_tablet_greater_than_desktop`; `tests/core/test_models.py::test_site_settings_homepage_project_count_accepts_valid_values` | Covered |
| `L-07` | `LAYOUT.md` | At a mobile viewport, cards after the configured `hp-mob-N` threshold are not displayed. | View test + direct CSS review | `tests/pages/test_views.py::test_homepage_grid_has_breakpoint_count_classes`; `apps/projects/static/css/project-cards.css` `@media (max-width: 639px)` `hp-mob-*` selector review (`2026-03-30`) | Partial |
| `L-08` | `LAYOUT.md` | At a tablet viewport, cards after the configured `hp-tab-N` threshold are not displayed. | View test + direct CSS review | `tests/pages/test_views.py::test_homepage_grid_has_breakpoint_count_classes`; `apps/projects/static/css/project-cards.css` `@media (min-width: 640px) and (max-width: 959px)` `hp-tab-*` selector review (`2026-03-30`) | Partial |
| `L-09` | `LAYOUT.md` | Desktop grid columns match the count-driven rules for `n1`, `n3`, `n5`, and `n6`. | View/context tests + direct CSS review | `apps/pages/templates/pages/home.html` `projects-grid--home-n{{ homepage_projects_count }}` review (`2026-03-30`); `tests/pages/test_views.py::test_homepage_query_respects_desktop_count`; `apps/projects/static/css/project-cards.css` desktop `projects-grid--home-n*` review (`2026-03-30`) | Partial |

## Hero States

| Matrix ID | Spec | State | Coverage mode | Current evidence | Status |
| --- | --- | --- | --- | --- | --- |
| `H-01` | `components/HERO.md` | Default hero renders title, two CTAs, scroll link, and standard density. | Browser smoke + visual audit | `tests/e2e/test_homepage.py::test_homepage_smoke`; `scripts/audit_hero_spec.py` cases `01-03` | Covered |
| `H-02` | `components/HERO.md` | Label-present state renders `.hero__label`. | View test | `tests/pages/test_views.py::test_hero_label_rendered_when_set` | Covered |
| `H-03` | `components/HERO.md` | Label-absent state omits `.hero__label`. | View test | `tests/pages/test_views.py::test_hero_label_absent_when_blank` | Covered |
| `H-04` | `components/HERO.md` | Tagline-absent state omits `.hero__subtitle`. | View test | `tests/pages/test_views.py::test_hero_tagline_absent_when_blank` | Covered |
| `H-05` | `components/HERO.md` | Compact mode adds `hero--compact` and uses the compact title scale. | View test + visual audit | `tests/pages/test_views.py::test_hero_compact_class_present_when_enabled`; `scripts/audit_hero_spec.py` case `06` | Covered |
| `H-06` | `components/HERO.md` | Background-image state uses the selected hero project cover image. | View/context tests | `tests/pages/test_views.py::test_homepage_context_exposes_hero_project`; `tests/pages/test_views.py::test_homepage_hero_renders_selected_cover_image_as_eager_background` | Covered |
| `H-07` | `components/HERO.md` | Placeholder background renders when no hero cover image exists. | Scripted visual audit | `scripts/audit_hero_spec.py` case `10` | Covered |
| `H-08` | `components/HERO.md` | Hero project comes from first featured project, or fallback homepage project when none are featured. | View/context tests | `tests/pages/test_views.py::test_homepage_context_exposes_hero_project`; `tests/pages/test_views.py::test_homepage_falls_back_to_recent_projects_when_none_are_featured` | Covered |
| `H-09` | `components/HERO.md` | Scroll affordance is visible above `639px` and hidden at `639px` and below. | Browser e2e | `tests/e2e/test_homepage.py::test_homepage_scroll_affordance_hides_at_mobile_breakpoint` | Covered |
| `H-10` | `components/HERO.md` | Reduced-motion state disables scroll-line animation and hero image transition. | Browser e2e | `tests/e2e/test_homepage.py::test_homepage_reduced_motion_disables_hero_animation_and_transition` | Covered |

## Navbar States

| Matrix ID | Spec | State | Coverage mode | Current evidence | Status |
| --- | --- | --- | --- | --- | --- |
| `N-01` | `components/NAVBAR.md` | Logo override suppresses text and monogram brand paths. | Scripted visual audit | `scripts/audit_nav_brand.py` cases `C`, `D`, `E-logo` | Covered |
| `N-02` | `components/NAVBAR.md` | `nav_name` override renders `.nav__name` and suppresses the monogram path. | View test | `tests/pages/test_views.py::test_nav_renders_nav_name_when_set`; `tests/pages/test_views.py::test_nav_nav_name_suppresses_monogram` | Covered |
| `N-03` | `components/NAVBAR.md` | Safe short `site_name` renders full text in `.nav__name`. | View test | `tests/pages/test_views.py::test_nav_renders_full_text_when_site_name_fits` | Covered |
| `N-04` | `components/NAVBAR.md` | Long or multi-word `site_name` renders `.nav__monogram`. | View test + unit test | `tests/pages/test_views.py::test_nav_renders_monogram_when_site_name_too_long`; `tests/pages/test_views.py::test_nav_monogram_triggered_by_word_count`; `tests/core/test_templatetags.py` | Covered |
| `N-05` | `components/NAVBAR.md` | Brand anchor always exposes the full name via `aria-label`. | View test | `tests/pages/test_views.py::test_nav_monogram_has_aria_label`; `tests/pages/test_views.py::test_nav_full_text_has_aria_label` | Covered |
| `N-06` | `components/NAVBAR.md` | Transparent home state inverts brand treatment to white before scroll/menu open. | Scripted visual audit | `scripts/audit_nav_brand.py` cases `D` and `D-text` | Covered |
| `N-07` | `components/NAVBAR.md` | Scrolled state applies solid blurred header treatment after `scrollY > 60`. | Browser e2e | `tests/e2e/test_navigation.py::test_header_gains_and_loses_scrolled_state_on_scroll` | Covered |
| `N-08` | `components/NAVBAR.md` | Mobile closed state shows the toggle and keeps links hidden with `aria-expanded=false`. | Browser e2e | `tests/e2e/test_navigation.py::test_mobile_navigation_opens_closes_and_navigates` | Covered |
| `N-09` | `components/NAVBAR.md` | Mobile open state shows the overlay and locks body scroll. | Browser e2e + visual audit | `tests/e2e/test_navigation.py::test_mobile_navigation_opens_closes_and_navigates`; `scripts/audit_nav_brand.py` cases `E` and `E-logo` | Covered |
| `N-10` | `components/NAVBAR.md` | `Escape` closes the menu and returns focus to the toggle. | Browser e2e | `tests/e2e/test_navigation.py::test_mobile_navigation_keyboard_focus_moves_into_menu_and_returns_on_escape` | Covered |
| `N-11` | `components/NAVBAR.md` | Breakpoint recovery closes an open mobile menu above `767px`. | Browser e2e | `tests/e2e/test_navigation.py::test_mobile_navigation_recovers_when_viewport_crosses_breakpoint` | Covered |
| `N-12` | `components/NAVBAR.md` | Tablet and desktop use inline links and hide the toggle. | Browser e2e | `tests/e2e/test_navigation.py::test_tablet_navigation_uses_inline_links` | Covered |
| `N-13` | `components/NAVBAR.md` | Current route gets `.is-active`; Contact keeps desktop CTA styling and mobile overlay reset styling. | View test + browser e2e | `tests/pages/test_views.py::test_nav_marks_current_route_active`; `tests/e2e/test_navigation.py::test_contact_nav_cta_keeps_desktop_style_and_resets_in_mobile_overlay` | Covered |

## Admin Safety States

| Matrix ID | Spec | State | Coverage mode | Current evidence | Status |
| --- | --- | --- | --- | --- | --- |
| `A-01` | Current admin implementation | Admin warns when `site_name` is blank. | Admin test | `tests/core/test_admin.py::test_site_settings_admin_warns_when_site_name_blank` | Covered |
| `A-02` | Current admin implementation | Admin warns when `contact_email` is blank. | Admin test | `tests/core/test_admin.py::test_site_settings_admin_warns_when_contact_email_blank` | Covered |
| `A-03` | Current admin implementation | Admin shows info when `site_name` exceeds `30` characters and no `nav_name` or `logo` is set. | Admin test | `tests/core/test_admin.py::test_site_settings_admin_informs_when_site_name_is_long_without_nav_name_or_logo` | Covered |
| `A-04` | Current admin implementation | Admin warns when the computed automatic monogram would collapse to one letter and no override is set. | Admin test | `tests/core/test_admin.py::test_site_settings_admin_warns_when_monogram_would_collapse_to_single_letter` | Covered |
| `A-05` | Current admin implementation | `Site Settings` shows a launch-readiness summary in admin. | Admin test | `tests/core/test_admin.py::test_site_settings_admin_launch_readiness_surfaces_homepage_fallback_warning` | Covered |
| `A-06` | Current readiness implementation | Launch readiness warns when a long `site_name` has no `nav_name` or `logo`. | Management-command test | `tests/core/test_management_commands.py::test_readiness_warns_when_long_site_name_has_no_nav_name_or_logo` | Covered |
| `A-07` | Current readiness implementation | Launch readiness warns when no projects are marked featured. | Management-command test | `tests/core/test_management_commands.py::test_readiness_warns_when_no_featured_projects_are_selected` | Covered |
| `A-08` | Current readiness implementation | Launch readiness warns when the current homepage hero project has no cover image. | Management-command test | `tests/core/test_management_commands.py::test_readiness_warns_when_current_homepage_hero_project_has_no_cover_image` | Covered |
| `A-09` | Current admin/readiness implementation | Admin and launch readiness distinguish public contact details from the internal notification inbox configuration. | Admin test + management-command test | `tests/core/test_admin.py::test_site_settings_admin_warns_when_notification_inbox_missing`; `tests/core/test_management_commands.py::test_readiness_warns_when_internal_contact_notification_inbox_is_missing` | Covered |
| `A-10` | Current admin implementation | Admin help text warns that share, cover, and gallery images are served directly and should be upload-optimized. | Admin test | `tests/core/test_admin.py::test_site_settings_admin_help_text_highlights_brand_and_contact_setup`; `tests/projects/test_admin.py::test_project_admin_help_text_highlights_cover_image_quality`; `tests/projects/test_admin.py::test_project_image_inline_help_text_highlights_direct_delivery_and_ordering` | Covered |

## Contact Flow States

| Matrix ID | Spec | State | Coverage mode | Current evidence | Status |
| --- | --- | --- | --- | --- | --- |
| `C-01` | Current contact implementation | With a configured notification inbox, a valid submission saves the inquiry and redirects to the sent success state. | Form/view test + browser e2e | `tests/contact/test_forms.py::test_contact_form_valid_post_creates_inquiry`; `tests/e2e/test_contact.py::test_contact_form_submit_reaches_success_page` | Covered |
| `C-02` | Current contact implementation | Invalid or expired submission tokens show an actionable reload-and-try-again message and do not save an inquiry. | Form test | `tests/contact/test_forms.py::test_contact_form_invalid_token_uses_actionable_reload_message` | Covered |
| `C-03` | Current contact implementation | Blank `CONTACT_EMAIL` skips the send attempt, logs a warning, saves the inquiry, and redirects to the saved-only success state. | Form/view test | `tests/contact/test_forms.py::test_contact_form_saves_inquiry_without_send_when_contact_email_missing` | Covered |
| `C-04` | Current contact implementation | Delivery failure still saves the inquiry, logs the failure, and redirects to the saved-only success state. | Form/view test | `tests/contact/test_forms.py::test_contact_form_saves_inquiry_even_when_email_send_fails` | Covered |
| `C-05` | Current contact implementation | The success page branches between normal sent copy and calm saved-only copy. | View test | `tests/contact/test_views.py::test_contact_success_page`; `tests/contact/test_views.py::test_contact_success_page_saved_only_state` | Covered |

## Image Delivery States

| Matrix ID | Spec | State | Coverage mode | Current evidence | Status |
| --- | --- | --- | --- | --- | --- |
| `I-01` | Current image implementation | Homepage hero image uses eager loading, `fetchpriority="high"`, and real intrinsic dimensions when valid metadata is available. | View test | `tests/pages/test_views.py::test_homepage_hero_renders_selected_cover_image_as_eager_background`; `tests/pages/test_views.py::test_homepage_hero_and_featured_cards_emit_image_dimensions_and_priority` | Covered |
| `I-02` | Current image implementation | Project card preview images emit real intrinsic dimensions when valid metadata is available and keep lazy loading with async decoding. | View test | `tests/pages/test_views.py::test_homepage_hero_and_featured_cards_emit_image_dimensions_and_priority`; `tests/projects/test_views.py::test_project_list_preview_images_emit_real_dimensions_when_available`; `tests/projects/test_views.py::test_project_detail_related_preview_images_emit_real_dimensions_when_available` | Covered |
| `I-03` | Current image implementation | Project detail hero image uses the resolved detail-media source with `fetchpriority="high"` and real intrinsic dimensions when valid metadata is available. | View test | `tests/projects/test_views.py::test_project_detail_uses_first_gallery_image_for_hero_and_og_when_cover_missing` | Covered |
| `I-04` | Current image implementation | Project gallery and supporting-media images emit real intrinsic dimensions when valid metadata is available and keep lazy loading with async decoding. | View test | `tests/projects/test_views.py::test_project_detail_labels_non_gallery_media_with_truthful_section_heading` | Covered |

## Project Detail States

| Matrix ID | Spec | State | Coverage mode | Current evidence | Status |
| --- | --- | --- | --- | --- | --- |
| `P-01` | Current project implementation | Project detail hero and share media resolve through one path: `cover_image`, then first gallery image, then no-image state. | View test | `tests/projects/test_views.py::test_project_detail_uses_first_gallery_image_for_hero_and_og_when_cover_missing`; `tests/projects/test_views.py::test_project_detail_og_image_falls_back_to_site_settings` | Covered |
| `P-02` | Current project implementation | Non-gallery project media render under a truthful shared supporting-media heading. | View test | `tests/projects/test_views.py::test_project_detail_labels_non_gallery_media_with_truthful_section_heading` | Covered |
| `P-03` | Current project implementation | The detail-page contact CTA carries the current project category into the contact-form `project_type` prefill. | View test | `tests/projects/test_views.py::test_project_detail_cta_prefills_contact_project_type_from_category` | Covered |
