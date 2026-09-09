import SwiftUI

@main
struct AssumptionApp: App {
    @State private var coordinator = AppCoordinator(services: ServiceContainer())

    var body: some Scene {
        WindowGroup {
            RootView()
                .environment(coordinator)
                .environment(coordinator.services.language)
        }
    }
}
