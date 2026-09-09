import SwiftUI

/// Switches content language. Costs no network: the server sends all three at
/// once, so this only changes which one is drawn.
struct LanguageMenu: View {
    @Environment(LanguagePreference.self) private var language

    var body: some View {
        @Bindable var language = language

        Menu {
            Picker("Language", selection: $language.current) {
                ForEach(ContentLanguage.allCases) { candidate in
                    Text(candidate.displayName).tag(candidate)
                }
            }
        } label: {
            Text(language.current.shortName)
                .font(Typography.data(12))
        }
    }
}
