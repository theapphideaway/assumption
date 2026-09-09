import SwiftUI

/// Dispatches one block to its view.
///
/// The `unknown` case is deliberate: if the server gains a block type before
/// this build does, it renders as plain text rather than vanishing. An old app
/// must never silently drop a line of a prayer.
struct BlockView: View {
    let block: Block

    var body: some View {
        switch block.kind {
        case .heading: HeadingBlockView(block: block)
        case .rubric: RubricBlockView(block: block)
        case .paragraph: ParagraphBlockView(block: block)
        case .refrain: RefrainBlockView(block: block)
        case .hymn: HymnBlockView(block: block)
        case .psalm: PsalmBlockView(block: block)
        case .verse: VerseBlockView(block: block)
        case .silence: SilenceBlockView()
        case .dismissal: DismissalBlockView(block: block)
        case .unknown: UnknownBlockView(block: block)
        }
    }
}
