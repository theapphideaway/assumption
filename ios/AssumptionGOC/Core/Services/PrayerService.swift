import Foundation

/// The day's prayer rule, already assembled by the server.
protocol PrayerServicing: Sendable {
    func rule(for date: Date?) async throws -> PrayerResponse
}

struct PrayerService: PrayerServicing {
    private let client: APIClientProtocol

    init(client: APIClientProtocol) { self.client = client }

    func rule(for date: Date? = nil) async throws -> PrayerResponse {
        let endpoint = date.map { Endpoint.prayers(date: ISODate.string(from: $0)) }
            ?? .prayers
        return try await client.get(endpoint, as: PrayerResponse.self)
    }
}
