import SwiftUI

struct HeadingBlockView: View {
    let block: Block

    var body: some View {
        if let text = block.text {
            LocalizedTextView(text: text, size: 19)
                .fontWeight(.semibold)
                .padding(.top, 12)
        }
    }
}
