import SwiftUI

struct DismissalBlockView: View {
    let block: Block

    var body: some View {
        if let text = block.text {
            VStack(alignment: .leading, spacing: 10) {
                Divider()
                LocalizedTextView(text: text)
                    .lineSpacing(5)
            }
            .padding(.top, 10)
        }
    }
}
