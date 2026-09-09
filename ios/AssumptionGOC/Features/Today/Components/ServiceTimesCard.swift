import SwiftUI

struct ServiceTimesCard: View {
    let services: [ServiceTime]

    @Environment(LanguagePreference.self) private var language

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("SERVICES TODAY")
                .font(Typography.data(10))
                .foregroundStyle(.secondary)
            ForEach(services) { service in
                HStack {
                    Text(service.title.resolved(language.current))
                        .font(Typography.ui(14))
                    Spacer()
                    Text(service.time)
                        .font(Typography.data(13))
                        .foregroundStyle(LiturgicalPalette.gold)
                }
            }
        }
        .padding(16)
        .frame(maxWidth: .infinity, alignment: .leading)
        .overlay(RoundedRectangle(cornerRadius: 6).stroke(.quaternary))
    }
}
