import Foundation

enum APIError: LocalizedError, Equatable {
    case offline
    case badResponse(status: Int)
    case decoding(String)
    case invalidURL

    /// Written from the reader's side of the screen: what went wrong and what
    /// they can do, never a status code on its own.
    var errorDescription: String? {
        switch self {
        case .offline:
            "No connection. Showing what was saved on this device."
        case .badResponse(let status) where status >= 500:
            "The parish server is having trouble. Try again in a moment."
        case .badResponse:
            "That could not be loaded."
        case .decoding:
            "The parish server sent something this version does not understand. Updating the app may help."
        case .invalidURL:
            "That address is not valid."
        }
    }
}
