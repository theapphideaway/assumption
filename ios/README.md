# Assumption GOC — iOS

SwiftUI, MVVM-C. iOS 17+ (uses `@Observable`).

## Creating the Xcode project

There is no `.xcodeproj` in the repo — generated project files churn badly in
git. Create one once:

1. Xcode → **New Project → iOS → App**. Name it `AssumptionGOC`, interface
   SwiftUI, language Swift, storage None.
2. Save it so the project file sits at `ios/AssumptionGOC.xcodeproj`, alongside
   the existing `AssumptionGOC/` source folder.
3. Delete the `ContentView.swift` and `AssumptionGOCApp.swift` Xcode generated —
   `App/AssumptionApp.swift` replaces them.
4. Drag the `AssumptionGOC` folder into the project navigator. Choose **Create
   groups**, and leave "Copy items if needed" UNCHECKED so the files stay where
   git tracks them.
5. Set the deployment target to iOS 17.

## Layers

    App/          coordinator, routes, tab shell
    Core/
      Models/     Codable mirrors of the API. No behaviour beyond decoding.
      Networking/ APIClient, endpoints, errors. Nothing else builds URLs.
      Services/   one per API area; the only layer that touches APIClient
      Design/     palette and type roles
    Features/     a view + a view model per screen, components in Components/
    Shared/       the block renderer, used by prayers, readings and scripture

The rule the code follows: **views hold view logic only.** Date formatting,
slot selection, which card appears, what an error says — all of that is on the
view model. Views read properties and call closures.

Views never construct their own dependencies either. `AppCoordinator` builds
view models, so a screen can be handed a test double without touching a
singleton.

## The block renderer

`Shared/BlockRenderer` is the reusable core. Documents arrive as a FLAT array
of typed blocks — the server has already spliced in shared sections, filled the
day's propers and baked psalm text — so rendering is a `ForEach` and a `switch`
rather than recursive views.

`Block.Kind.unknown` is deliberate: a type this build does not know renders as
plain text rather than vanishing. An old app must never silently drop a line of
a prayer.

## Fonts

`Typography.bundledFontsAvailable` is `false` and falls back to system serif.
Before release, add **Gentium Book Plus** (Greek), **EB Garamond** (display)
and **Ponomar Unicode** (Church Slavonic), register them in Info.plist under
`UIAppFonts`, and flip the flag. Slavonic in a system face loses its pointing,
and the failure is ugly and silent — check it on a real device early.

## Server

`AppConfiguration.baseURL` points at the PythonAnywhere host. Every endpoint
keeps its **trailing slash**: Django redirects without one, so a missing slash
silently costs an extra round trip on every request.

## Not in version one

Scripture browsing, commemoration submission, parish pages and push. The first
two need only screens; the last two need server models and the paid plan.
