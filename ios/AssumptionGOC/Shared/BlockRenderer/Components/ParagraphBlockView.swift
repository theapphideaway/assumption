import SwiftUI

struct ParagraphBlockView: View {
    let block: Block

    var body: some View {
        if let text = block.text {
            LocalizedTextView(text: text)
                .lineSpacing(5)
        }
    }
}
