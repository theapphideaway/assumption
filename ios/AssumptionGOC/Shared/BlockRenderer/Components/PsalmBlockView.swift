import SwiftUI

/// A psalm as the prayer book prints it.
///
/// The text is baked in from each tradition's own psalter — the Slavonic from
/// the Church Slavonic psalter, the English from Brenton — never fetched from a
/// Bible at render time. A rule shows the psalm its own book prints.
struct PsalmBlockView: View {
    let block: Block

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            if let reference = block.reference {
                Text(reference)
                    .font(Typography.data(11))
                    .foregroundStyle(.secondary)
            }
            if let text = block.text {
                LocalizedTextView(text: text, size: 17)
                    .lineSpacing(5)
            }
        }
    }
}
