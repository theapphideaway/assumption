import SwiftUI

/// Renders a document.
///
/// Documents are a flat array, so this is a ForEach and nothing more. The
/// reusable core of the app: prayers, the day's readings and Bible chapters all
/// come through here.
struct BlockListView: View {
    let blocks: [Block]
    var spacing: CGFloat = 14

    var body: some View {
        LazyVStack(alignment: .leading, spacing: spacing) {
            ForEach(blocks) { block in
                BlockView(block: block)
            }
        }
    }
}
