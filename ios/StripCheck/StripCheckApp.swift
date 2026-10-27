import SwiftUI

@main
@MainActor
struct StripCheckApp: App {
    @StateObject private var model = AppModel()
    var body: some Scene {
        WindowGroup {
            RootView().environmentObject(model).tint(Color(red: 0.10, green: 0.29, blue: 0.78))
        }
    }
}
