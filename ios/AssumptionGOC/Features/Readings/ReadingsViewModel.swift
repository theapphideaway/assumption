import Foundation
import Observation

/// The day's readings, with their text.
@Observable
@MainActor
final class ReadingsViewModel {
    enum State { case loading, loaded, failed(String) }

    private(set) var state: State = .loading
    private(set) var readings: ReadingSet?
    private(set) var dayTitle: LocalizedText?

    private let prayers: PrayerServicing
    private let isoDate: String

    init(prayers: PrayerServicing, isoDate: String) {
        self.prayers = prayers
        self.isoDate = isoDate
    }

    func load() async {
        state = .loading
        do {
            let response = try await prayers.rule(for: ISODate.date(from: isoDate))
            readings = response.day.readings
            dayTitle = response.day.title
            state = .loaded
        } catch {
            state = .failed((error as? APIError)?.errorDescription
                            ?? "The readings could not be loaded.")
        }
    }

    var gospelVerses: [Block] { verses(from: readings?.gospelText) }
    var epistleVerses: [Block] { verses(from: readings?.epistleText) }
    var gospelReference: String? { readings?.gospel }
    var epistleReference: String? { readings?.epistle }

    var entries: [ReadingEntry] { readings?.entries ?? [] }

    /// Where the server holds no references, it still says what is appointed
    /// and at which services — never that nothing is.
    var unsourcedNote: String? {
        guard readings?.status == .unsourced else { return nil }
        return readings?.note
    }

    private func verses(from source: [Verse]?) -> [Block] {
        guard let source, let data = try? JSONEncoder().encode(
            source.map { VerseBlockPayload(type: "verse", n: $0.n, text: $0.text) })
        else { return [] }
        return (try? JSONDecoder().decode([Block].self, from: data)) ?? []
    }

    private struct VerseBlockPayload: Encodable {
        let type: String
        let n: Int
        let text: LocalizedText
    }
}
