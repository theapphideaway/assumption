import SwiftUI

/// A block type this build does not know.
///
/// Rendered as plain text rather than dropped. If the server adds a type before
/// the app updates, the reader gets an unstyled line — never a missing one.
struct UnknownBlockView: View {
    let block: Block

    var body: some View {
        if let text = block.text {
            LocalizedTextView(text: text)
        }
    }
}
