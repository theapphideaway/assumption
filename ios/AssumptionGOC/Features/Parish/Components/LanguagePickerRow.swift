import SwiftUI

struct LanguagePickerRow: View {
    @Environment(LanguagePreference.self) private var language

    var body: some View {
        @Bindable var language = language

        Picker("Content language", selection: $language.current) {
            ForEach(ContentLanguage.allCases) { candidate in
                Text(candidate.displayName).tag(candidate)
            }
        }
    }
}
