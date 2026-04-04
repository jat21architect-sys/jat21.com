# Customization

This guide is for buyers and operators, not maintainers. It explains what you can change safely in admin, what needs extra care before publishing, and what still requires developer or environment access.

## What You Can Change Safely In Admin

| Area | What you can change | Where |
| --- | --- | --- |
| Brand basics | Practice name, tagline, hero label, compact hero mode, nav abbreviation, logo, default share image | `Site Settings` |
| Public contact details | Public email, phone, location, and social links | `Site Settings` |
| Stored contact record | Address, for internal recordkeeping only in the current implementation | `Site Settings` |
| Search/share metadata | Homepage and per-page meta descriptions, GA4 measurement ID | `Site Settings` |
| Homepage density | How many featured projects show on mobile, tablet, and desktop | `Site Settings` |
| About page | Studio/person mode, principal details, practice summary, approach, profile facts, portrait, CV file | `About Profile` |
| Services page | Service titles, summaries, descriptions, order, active/inactive state | `Services` |
| Project portfolio | Project content, images, testimonials, feature flags, ordering, SEO overrides | `Projects` |
| Enquiry workflow | Inquiry status and internal notes | `Contact Inquiries` |

## Changes That Need A Quick QA Check

| Change | Why it needs checking | What to verify |
| --- | --- | --- |
| Long `site_name` | It affects hero fit and automatic navbar brand fallback | Homepage hero wrap, navbar brand path, footer brand |
| Adding or removing `nav_name` | It changes whether the navbar shows full text or a monogram | Desktop navbar, mobile menu-open state, transparent home header |
| Uploading a logo | It overrides all text branding and is width-capped in the navbar | Transparent home header, scrolled header, mobile menu-open state |
| Leaving `contact_email` blank | It removes the main public email contact from the footer and contact page | Footer contact area and contact page |
| Changing contact delivery environment settings | It changes whether contact-form notifications are actually delivered internally | `Launch Readiness`, Site Settings admin warnings, contact-form submit result |
| Turning on `hero_compact` | It changes the homepage hero title scale | Homepage hero at desktop, tablet, and mobile |
| Changing homepage project counts | It changes how many cards appear per breakpoint | Homepage at mobile, tablet, and desktop |
| Changing About portrait mode or portrait image | It changes whether the portrait column and CV button appear | About page desktop and mobile |
| Changing the first featured project | That project can become the homepage hero image source | Homepage hero image and first featured card |
| Uploading a new cover image | It changes homepage hero, project detail hero, and project share image behavior when that project drives those surfaces | Homepage hero, project detail hero, social preview |
| Leaving a project cover image blank or reordering its gallery | It changes which image drives the project detail hero/share fallback | Project detail hero, share preview, first gallery image |
| Editing service slugs | Service enquiry links map contact prefill from the slug | “Discuss this service” link on the Services page |

## What Is Fixed Without Code Changes

| Surface | Current behavior |
| --- | --- |
| Navbar links | The site always ships with `Projects`, `About`, `Services`, and `Contact` in that order. |
| Hero CTA labels and routes | The homepage CTAs are fixed to `View Projects` and `Start a Conversation`. |
| Services page hero copy | The page title and introductory subtitle are hardcoded in the template. |
| Contact page hero copy | The page title and subtitle are hardcoded in the template. |
| Project categories | The public category system is fixed to `Housing`, `Civic`, and `Workplace`. |
| Fonts and color system | Controlled in CSS, not in admin. |

## Changes That Need Developer Or Environment Access

| Need | Why admin is not enough |
| --- | --- |
| Change fonts, color palette, spacing, or layout system | Those are defined in CSS and shared specs. |
| Add, remove, or rename navbar items | Navigation structure is hardcoded in the shared template. |
| Change homepage CTA labels or destinations | Those links are hardcoded in the homepage template. |
| Add new project categories | Category choices and filter behavior are defined in the model and views. |
| Change contact form fields, validation, or anti-spam timing | Those rules live in `ContactForm` and the contact template. |
| Change the inbox that receives contact-form notifications | That is the `CONTACT_EMAIL` environment variable, not `Site Settings.contact_email`. |
| Change email sender or SMTP delivery | Those are environment settings: `DEFAULT_FROM_EMAIL`, `EMAIL_BACKEND`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`. If they are missing or broken, the contact form still stores enquiries but switches to a saved-only success state. |
| Change file storage, Sentry, or production analytics plumbing | Those are environment/settings concerns, not admin content. |

## Practical Buyer Workflow

1. Start with `Site Settings`: set the real practice name, public email, location, meta description, and default share image.
2. Decide the navbar brand path early: leave it automatic, set a short `nav_name`, or upload a logo.
3. Complete `About Profile` before polishing portfolio pages. The About page has the most render gates.
4. Enter services before linking the site publicly. Service enquiry links are already wired into the contact form.
5. Add and order featured projects carefully. The first selected homepage project can become the homepage hero image source.
6. Before publishing, review the `Launch Readiness` panel in `Site Settings`, then run, or ask your maintainer to run, the content-readiness check for the same full result in the terminal.
7. Confirm both contact paths are ready: the public `contact_email` should look correct on the site, and the internal notification inbox `CONTACT_EMAIL` should be configured in the environment.

## Practical Warnings

| Situation | Recommendation |
| --- | --- |
| Your practice name is long | Expect to use `nav_name`, a logo, or both. |
| The public contact email is set but `CONTACT_EMAIL` is blank | The contact page can still look complete, but form notifications will not reach you. Set the internal inbox before launch. |
| You have not marked any projects as featured | The homepage will fall back to the first ordered projects until you choose featured work deliberately. |
| Your first homepage-driving project has no cover image | The homepage hero will use the placeholder background until that project gets a cover image or another project becomes first. |
| You upload huge original images straight from the camera or export tool | The current site serves uploaded images directly. Export web-sized versions before upload so hero and gallery surfaces stay fast. |
| A project has no cover image | The first gallery image becomes the detail hero/share fallback. Put the strongest landscape image first, or upload a dedicated cover image. |
| Your default share image is missing or poorly cropped | Pages without a page-specific share image will fall back to `Site Settings.og_image`, then the bundled default. Use a branded `1200×630` image for better previews. |
| You want a CV download on the About page | Use `portrait_mode=portrait` and upload both a portrait image and `cv_file`. In the current implementation, the CV button lives inside the portrait column. |
| You want the About CTA to read as one short headline | Keep `closing_invitation` at `80` characters or fewer. |
| You want the Services page enquiry links to prefill a specific project type | Keep service slugs aligned with the current built-in mapping. |
