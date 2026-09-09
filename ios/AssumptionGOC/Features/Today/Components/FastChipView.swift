import SwiftUI

/// The most-read thing in the app: whether today is a fast, and why.
struct FastChipView: View {
    let fast: Fast

    @Environment(LanguagePreference.self) private var language

    private var tint: Color {
        switch fast.level {
        case "STRICT": LiturgicalPalette.porphyry
        case "WINE_OIL", "DAIRY": LiturgicalPalette.verte
        case "FISH": LiturgicalPalette.lapis
        default: LiturgicalPalette.gold
        }
    }

    var body: some View {
        HStack(spacing: 6) {
            Text(fast.label.resolved(language.current))
                .font(Typography.ui(12, weight: .semibold))
            if let reason = fast.reason.text(in: language.current) {
                Text("· \(reason)")
                    .font(Typography.ui(12))
                    .foregroundStyle(.secondary)
            }
        }
        .padding(.horizontal, 10).padding(.vertical, 5)
        .background(tint.opacity(0.14), in: .rect(cornerRadius: 3))
        .foregroundStyle(tint)
        .overlay(RoundedRectangle(cornerRadius: 3).stroke(tint.opacity(0.35)))
    }
}
