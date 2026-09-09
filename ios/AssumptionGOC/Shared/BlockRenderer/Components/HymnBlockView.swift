import SwiftUI

struct HymnBlockView: View {
    let block: Block

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            if let tone = block.tone {
                Text("Tone \(tone)")
                    .font(Typography.data(11))
                    .foregroundStyle(LiturgicalPalette.gold)
            }
            if let text = block.text {
                LocalizedTextView(text: text)
                    .lineSpacing(5)
            }
        }
        .padding(.leading, 12)
        .overlay(alignment: .leading) {
            Rectangle()
                .fill(LiturgicalPalette.gold.opacity(0.5))
                .frame(width: 2)
        }
    }
}
