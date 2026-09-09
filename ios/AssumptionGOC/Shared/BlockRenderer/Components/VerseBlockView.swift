import SwiftUI

/// One verse of scripture, its number set superscript in the margin.
struct VerseBlockView: View {
    let block: Block

    var body: some View {
        if let text = block.text {
            HStack(alignment: .firstTextBaseline, spacing: 8) {
                Text("\(block.number ?? 0)")
                    .font(Typography.data(10))
                    .foregroundStyle(.secondary)
                    .frame(minWidth: 20, alignment: .trailing)
                    .accessibilityHidden(true)
                LocalizedTextView(text: text, size: 17)
                    .lineSpacing(4)
            }
            .accessibilityElement(children: .combine)
            .accessibilityLabel("Verse \(block.number ?? 0)")
        }
    }
}
