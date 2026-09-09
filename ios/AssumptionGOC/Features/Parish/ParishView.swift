import SwiftUI

/// Parish information.
///
/// Deliberately thin for version one: the server has no parish model yet, so
/// this shows what is known rather than inventing placeholders.
struct ParishView: View {
    var body: some View {
        List {
            Section {
                VStack(alignment: .leading, spacing: 4) {
                    Text(AppConfiguration.parishName).font(Typography.display(20))
                    Text(AppConfiguration.parishCity)
                        .font(Typography.ui(13))
                        .foregroundStyle(.secondary)
                }
                .padding(.vertical, 6)
            }

            Section("Language") {
                LanguagePickerRow()
            }

            Section {
                Text("Service times, photographs and ministries will appear here once the parish pages are added on the server.")
                    .font(Typography.ui(13))
                    .foregroundStyle(.secondary)
            }
        }
        .navigationTitle("Parish")
    }
}
