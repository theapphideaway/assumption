import Foundation

/// One place that builds services, so view models can be handed test doubles
/// without reaching for a singleton.
@MainActor
final class ServiceContainer {
    let calendar: CalendarServicing
    let prayers: PrayerServicing
    let announcements: AnnouncementServicing
    let language: LanguagePreference

    init(client: APIClientProtocol = APIClient(),
         language: LanguagePreference = LanguagePreference()) {
        self.calendar = CalendarService(client: client)
        self.prayers = PrayerService(client: client)
        self.announcements = AnnouncementService(client: client)
        self.language = language
    }

    init(calendar: CalendarServicing,
         prayers: PrayerServicing,
         announcements: AnnouncementServicing,
         language: LanguagePreference = LanguagePreference()) {
        self.calendar = calendar
        self.prayers = prayers
        self.announcements = announcements
        self.language = language
    }
}
