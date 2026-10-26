# Campus Marketplace identity

The new identity pairs a connected lowercase **cm** monogram with a two-line,
lowercase wordmark. Evergreen and warm ivory match the app's existing palette.
The wordmark is live HTML type, so it remains sharp on small and large displays,
uses the configured application name, and follows the light/dark theme.

The shared template is `frontend/templates/partials/_brand.html`. The header,
footer, favicon, and Apple touch icon now use this identity. Previous logo assets
remain available at their original paths.

## Assets

| File | Use |
| --- | --- |
| `campus-logo-light.png` | Complete transparent wordmark for light backgrounds |
| `campus-logo-dark.png` | Complete transparent wordmark for dark backgrounds |
| `campus-mark-master.png` | Original 1254 x 1254 artwork |
| `../../frontend/static/images/branding/campus-mark.png` | 96 x 96 header/footer artwork, displayed at 44 x 44 |
| `../../frontend/static/images/branding/favicon-32.png` | 32 x 32 browser tab icon |
| `../../frontend/static/images/branding/apple-touch-icon.png` | 180 x 180 home-screen icon |
| `../../frontend/static/images/branding/icon-512.png` | 512 x 512 general-purpose icon |

## Generation notes

Artwork was generated with the built-in image generation tool, using the imagegen
skill. Web exports are resampled copies of the selected artwork. Typography,
spacing, responsive sizing, and theme colors are implemented in HTML/CSS.
Complete wordmark PNGs are browser-rendered exports of the shared logo component.
The identity was checked at 1440 px and 390 px viewport widths and in both themes.

Final refinement prompt (the first generated monogram was supplied as a reference):

> Refine the supplied logo into a finished flat graphic app icon. Use the same
> lowercase cm monogram idea, but ensure the first letter is clearly an OPEN
> lowercase c with a visible opening on its right, and the m is clearly a double
> arch. Use thick, precisely drawn geometric letterforms with clean even edges and
> balanced spacing. Absolutely flatten the art: the ENTIRE square canvas must be a
> SINGLE perfectly uniform opaque solid evergreen color #17664b, right up to all
> four edges. Monogram in a SINGLE perfectly uniform warm ivory #f7f8f4. Exactly
> two flat solid colors apart from antialiased edges. Remove ALL shading, texture,
> grain, gradients, edge glow, shadows, lighting effects, vignettes, bevels, and
> translucent holes. There must be NO rounded outer tile shape, NO border, NO inset
> frame and NO transparency. It is a square uniform green field carrying the ivory
> cm letterform centered both vertically and horizontally, with even breathing room
> on all four sides. The letterform should fill about 70 percent of the square
> width. This is a flat production identity asset, like a professional typographic
> logo drawn in vector software. No additional objects, decorations or text.
