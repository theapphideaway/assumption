import Foundation
import Observation

/// The reader's chosen content language, remembered between launches.
///
/// Shared across every screen: switching language re-renders what is already in
/// memory rather than refetching, because the server sends all three at once.
@Observable
@MainActor
final class LanguagePreference {
    private static let storageKey = "content.language"

    var current: ContentLanguage {
        didSet { UserDefaults.standard.set(current.rawValue, forKey: Self.storageKey) }
    }

    init(defaults: UserDefaults = .standard) {
        let stored = defaults.string(forKey: Self.storageKey)
        current = stored.flatMap(ContentLanguage.init(rawValue:)) ?? .english
    }
}
