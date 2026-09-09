import Foundation
import Observation

/// One prayer document, open and being prayed.
@Observable
@MainActor
final class PrayerReaderViewModel {
    enum State { case loading, loaded, failed(String) }

    private(set) var state: State = .loading
    private(set) var document: PrayerDocument?

    private let prayers: PrayerServicing
    private let documentID: String
    private let isoDate: String?

    init(prayers: PrayerServicing, documentID: String, isoDate: String?) {
        self.prayers = prayers
        self.documentID = documentID
        self.isoDate = isoDate
    }

    func load() async {
        state = .loading
        do {
            let date = isoDate.flatMap(ISODate.date(from:))
            let response = try await prayers.rule(for: date)
            document = response.slots.values.flatMap { $0 }
                .first { $0.id == documentID }
            state = document == nil
                ? .failed("That prayer is not part of today's rule.")
                : .loaded
        } catch {
            state = .failed((error as? APIError)?.errorDescription
                            ?? "That prayer could not be loaded.")
        }
    }

    var title: String { document?.title ?? "" }
    var blocks: [Block] { document?.blocks ?? [] }

    /// Held on while a prayer is open. People pray with both hands occupied,
    /// and a display that sleeps mid-rule is a small cruelty.
    var keepsScreenAwake: Bool { true }
}
