import SwiftUI

/// Text in the reader's language, showing every language when they ask for it.
///
/// A missing language is shown as missing rather than quietly replaced: the
/// server never substitutes, and neither does this. Silent fallback means
/// nobody notices the gap and it never gets filled.
struct LocalizedTextView: View {
    let text: LocalizedText
    var size: CGFloat = 18
    var showsAllLanguages: Bool = false
    var color: Color = .primary

    @Environment(LanguagePreference.self) private var language

    var body: some View {
        if showsAllLanguages {
            VStack(alignment: .leading, spacing: 6) {
                ForEach(text.availableLanguages) { candidate in
                    line(candidate, emphasised: candidate == language.current)
                }
            }
        } else if let exact = text.text(in: language.current) {
            Text(exact)
                .font(Typography.body(size, language: language.current))
                .foregroundStyle(color)
        } else if !text.isEmpty {
            fallback
        }
    }

    private func line(_ candidate: ContentLanguage, emphasised: Bool) -> some View {
        Text(text.resolved(candidate))
            .font(Typography.body(emphasised ? size : size - 2, language: candidate))
            .foregroundStyle(emphasised ? color : color.opacity(0.65))
    }

    /// Marked, so the reader can see this is not their language rather than
    /// assuming the parish prays it this way.
    private var fallback: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(text.resolved(language.current))
                .font(Typography.body(size, language: text.availableLanguages.first ?? .english))
                .foregroundStyle(color)
            Text("Not yet available in \(language.current.displayName)")
                .font(Typography.ui(11))
                .foregroundStyle(.secondary)
        }
    }
}
