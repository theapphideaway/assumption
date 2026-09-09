import SwiftUI

struct ReadingSectionView: View {
    let label: String
    let reference: String?
    let verses: [Block]

    var body: some View {
        if let reference {
            VStack(alignment: .leading, spacing: 10) {
                Text(label.uppercased())
                    .font(Typography.data(10))
                    .foregroundStyle(LiturgicalPalette.gold)
                Text(reference)
                    .font(Typography.display(18))
                if verses.isEmpty {
                    Text("Text not available in the loaded editions.")
                        .font(Typography.ui(12))
                        .foregroundStyle(.secondary)
                } else {
                    BlockListView(blocks: verses, spacing: 8)
                }
            }
        }
    }
}
