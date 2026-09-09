import SwiftUI

/// A marked pause. Deliberately empty space rather than an instruction.
struct SilenceBlockView: View {
    var body: some View {
        Color.clear
            .frame(height: 28)
            .accessibilityLabel("A pause")
    }
}
