import Foundation
import Observation

/// The day's rule, grouped by time of day.
@Observable
@MainActor
final class PrayerRuleViewModel {
    enum State { case loading, loaded, failed(String) }

    private(set) var state: State = .loading
    private(set) var response: PrayerResponse?
    var selectedSlot: PrayerSlot = .morning

    private let prayers: PrayerServicing
    private let clock: () -> Date

    init(prayers: PrayerServicing, clock: @escaping () -> Date = Date.init) {
        self.prayers = prayers
        self.clock = clock
    }

    func load() async {
        state = .loading
        do {
            let response = try await prayers.rule(for: nil)
            self.response = response
            selectedSlot = PrayerSlot.forHour(
                Calendar.current.component(.hour, from: clock()))
            state = .loaded
        } catch {
            state = .failed((error as? APIError)?.errorDescription
                            ?? "The prayer rule could not be loaded.")
        }
    }

    var slots: [PrayerSlot] {
        PrayerSlot.allCases.filter { !(response?.documents(for: $0).isEmpty ?? true) }
    }

    var documents: [PrayerDocument] { response?.documents(for: selectedSlot) ?? [] }

    var dayTitle: LocalizedText? { response?.day.title }

    /// Content the server could not supply, surfaced rather than hidden. Today
    /// this is the troparion of the day, which is not yet on file.
    var unavailableNote: String? {
        guard let missing = response?.missing, !missing.isEmpty else { return nil }
        let kinds = Set(missing.map(\.kind))
        guard kinds.contains("proper") else { return nil }
        return "The troparion of the day is not yet available."
    }
}
