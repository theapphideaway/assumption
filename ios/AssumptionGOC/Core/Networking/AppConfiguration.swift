import Foundation

/// Where the app points, and the few values that are not the server's business.
enum AppConfiguration {
    static let baseURL = URL(string: "https://ianschoenrockpersonal.pythonanywhere.com")!

    /// How far either side of today the client caches resolved days. Wide
    /// enough to span the next Pascha in both directions, so the calendar never
    /// shows an empty stretch offline.
    static let cacheWindowDays = 400

    static let parishName = "Assumption Greek Orthodox Church"
    static let parishCity = "Pocatello, Idaho"
}
