import SwiftUI

/// An instruction, not a prayer.
///
/// Red and italic, which liturgical books have done for a thousand years — the
/// one piece of typographic hierarchy the tradition hands us already solved.
struct RubricBlockView: View {
    let block: Block

    var body: some View {
        if let text = block.text {
            LocalizedTextView(text: text, size: 14, color: LiturgicalPalette.cinnabar)
                .italic()
        }
    }
}
