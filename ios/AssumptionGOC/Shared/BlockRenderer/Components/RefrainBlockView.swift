import SwiftUI

/// A short line said a set number of times.
///
/// The count is printed once rather than the line repeated, and there is no
/// tap-counter. Prayer is not a habit-tracking problem, and a counter turns
/// something received into something scored.
struct RefrainBlockView: View {
    let block: Block

    private var repetitions: Int { max(block.times ?? 1, 1) }

    var body: some View {
        if let text = block.text {
            HStack(alignment: .firstTextBaseline, spacing: 10) {
                LocalizedTextView(text: text)
                if repetitions > 1 {
                    Text("×\(repetitions)")
                        .font(Typography.data(12))
                        .foregroundStyle(.secondary)
                        .accessibilityLabel("said \(repetitions) times")
                }
            }
        }
    }
}
